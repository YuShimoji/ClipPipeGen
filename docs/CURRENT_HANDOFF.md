---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_M2_ACCEPTED_M3_READY_FOR_EXPLICIT_MAIN_INTEGRATION_V1
last_touched: 2026-07-25
current_slice: OUT-13
phase: main_integration_preflight_active
canonical_status: m2_accepted_m3_ready_for_explicit_main_integration
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
sync_baseline_head: e0279d513e89fac833d0c7415dc3234d00946773
verified_implementation_head: e0279d513e89fac833d0c7415dc3234d00946773
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 candidate 005 is accepted for the recorded internal editorial scope; M3 is ready for explicit main integration
human_entrypoint: docs/output_layer/out13_human_acceptance_receipt.json
portable_entrypoint: docs/output_layer/out13_human_acceptance_receipt.json
review_open_command: powershell -NoProfile -Command Invoke-Item docs\output_layer\out13_human_acceptance_receipt.json
review_server_restart_command: null
machine_readback: docs/output_layer/out13_human_acceptance_receipt.json
decision_required: explicit_main_integration_authorization
review_status: accepted_internal_exact_media_sha_and_recorded_dimensions
remote_code_complete: true
local_artifact_available: true
local_artifact_role: accepted_exact_candidate_005_same_machine_evidence
portable_local_artifact_available: false
cross_machine_resume_class: tracked_acceptance_receipt_and_code_are_portable_private_media_and_generated_package_are_not
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: false
automation_acceptance_granted: true
automation_acceptance_scope: tracked_builder_plus_current_host_exact_resume_package_hash_and_http_readback
editorial_acceptance_granted: true
acceptance_receipt: docs/output_layer/out13_human_acceptance_receipt.json
acceptance_review_context_id: out13_candidate_005_internal_full_view_editorial_visual_review_v1
acceptance_media_sha256: a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5
acceptance_dimensions: editorial_composition, editorial_flow, subtitle_presentation, picture_quality_for_internal_editorial_use, audio_quality_for_internal_editorial_use
same_review_identity_reopens_human_review: false
bounded_repair_reopens_only_affected_dimensions_and_timestamps: true
main_integration_approved: false
main_integration_preflight_verdict: READY_FOR_EXPLICIT_MAIN_INTEGRATION
next_action: request_explicit_main_integration_authorization_without_reopening_human_review
active_artifact: clip-out13-editorial-video-candidate-v1-005
source_of_truth: true
owner_lane: editorial_acceptance_and_main_integration_preflight
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, docs/output_layer/out13_human_acceptance_receipt.json, artifacts/ARTIFACTS.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## M2は受領済み、M3は統合前監査中

2026-07-25 JST、ユーザーは
`clip-out13-editorial-video-candidate-v1-005`のexact final MP4
SHA `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`
へ`accept`を与えた。受領対象は、従来手順で全編確認した内部editorial / visual
reviewであり、構成、編集フロー、字幕提示、内部用途の画質・音質に限定される。
判断主体、日付、context、media/package/implementation identityの分離は
[out13_human_acceptance_receipt.json](output_layer/out13_human_acceptance_receipt.json)に記録した。

M2はclosedである。もう一度の全編視聴、candidate 006、追加renderは不要。
candidate 004と005のfinal MP4は同じSHAで、同じreview context・同じ判断次元を持つため、
004側にも新しいreview gateを作らない。package revisionまたはimplementation revisionだけが
変わっても受領は失効しない。

## 受領の継承境界

| 変化 | 既存受領 | 再確認範囲 |
|---|---|---|
| media SHA、review context、判断次元が同じ | 継承 | なし |
| package revisionだけが変わる | 継承 | なし |
| implementation revisionだけが変わる | 継承 | なし |
| 字幕など一つの判断次元をbounded repair | 影響しない次元は継承 | 変えた、または因果的に影響する次元だけ |
| timestampで限定できるrepair | 該当外intervalは継承 | 影響intervalだけ |
| media SHAが変わる | 同じmedia identityとしては継承しない | 新しいreview identityを起票 |

このルールは「実装commitが進んだ」という理由だけでaccepted mediaを
`human_review_pending`へ戻すことを防ぐ。新しい実害または媒体変更がある場合だけ、
範囲を限定して判断を再開する。

## M3 main integration preflight

active branchは`codex/out-13-editorial-video-candidate-v1`。監査開始時点のfeature tipは
`d753ea7bb4b48bb98da1fc16afc073d20432acb1`、`origin/main`は
`5d6f69a64d510508a1f78ab3111a7780913a019c`で、feature branchに取り込み済みである。
開始時のupstream parityは`0 0`、tracked worktreeはclean、`git ls-files episodes`は0件。

M3ではbranch全差分、product code / tests / docs / generated / ignoredの境界、
credentials・private media・machine-specific pathの混入、現在状態とOUT-13の回帰、
静的検査を確認した。判定は`READY_FOR_EXPLICIT_MAIN_INTEGRATION`でcurrent blockerはない。
明示承認なしにmainへmergeまたはpushしない。

## 技術claimの適用範囲

OUT-13 packageの保全claimは、このリポジトリのローカル実行経路を対象にする。
通常ファイル、正規化path、既存のsymlink/junction拒否、manifest/file hash、
package-tree digestによるexact-byte/content consistencyが監査対象である。
権限を持つ外部process、filesystem/OS侵害、監査外の同時改変まで防ぐ一般セキュリティ保証は
ここから主張しない。それらは今回のmain統合を止めないnonblocking debtである。

## 保護対象と未承認gate

candidate 003 / 004 / 005のplan、caption、manifest、package、MP4はignored read-only evidence。
`episodes/`を広域cleanupせず、tracked fileを作らない。受領receiptはGitでportableだが、
private mediaとgenerated packageはGit cloneへ移らない。

以下はM2受領に含まれない。

- rights approval
- production subtitle/design/render acceptance
- production image quality acceptance
- thumbnail acceptance
- publishing、upload、public release
- main integration

## 再開手順

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
git ls-files episodes
```

続いて`docs/SUPERVISOR_STATUS_REPORT.md`のM3 verdictと
`docs/output_layer/out13_human_acceptance_receipt.json`を確認する。
同じmedia SHA・context・accepted dimensionsへ人間reviewを再要求しない。
