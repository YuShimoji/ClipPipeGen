---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: recovery_ready
health: OUT08_PRIVATE_REVIEW_PACKAGE_RECOVERY_READY
progress_pct: 100
last_touched: 2026-07-15
current_slice: OUT-08
phase: private_artifact_recovery
canonical_status: exact_candidates_review_ready_on_last_verified_host
active_branch: codex/out-08-private-review-package-recovery-v0
verified_source_head: b747705c7f7500071787fdba55048f4df6721b47
remote_resume_contract: pull_current_active_branch_tip_then_read_this_file
current_title: OUT-08 exact private review package recovery
human_entrypoint: null
portable_entrypoint: null
review_open_command: null
machine_readback: null
decision_required: perform_one_private_package_transfer
review_status: OUT08_PRIVATE_REVIEW_PACKAGE_RECOVERY_READY
remote_code_complete: true
local_artifact_available: false
portable_local_artifact_available: false
cross_machine_resume_class: private_package_transfer_required
active_rebuild_contract: null
parked_predecessor_rebuild_contract: artifacts/ACTIVE_REBUILD.json
current_host: DESKTOP-U9P4LKJ
current_host_package_status: package_missing
current_host_access_status: recovery_kit_ready_package_not_yet_imported
last_verified_host: DESKTOP-H53P1T4
last_verified_host_label: Thank
last_verified_host_local_artifact_available: true
last_verified_host_entrypoint: http://127.0.0.1:8071/index.html
review_server_status: server_stopped
host_probe_command: uvx python -m src.cli.main recover-out08-private-review-package --format json probe
private_export_command: uvx python -m src.cli.main recover-out08-private-review-package --format json export --destination D:\private-transfer\out08-review.zip
private_import_command: uvx python -m src.cli.main recover-out08-private-review-package --format json import --archive D:\private-transfer\out08-review.zip --start-server
recovery_contract: docs/output_layer/out08_private_review_package_recovery_contract.json
recovery_operator_guide: docs/output_layer/OUT_08_PRIVATE_REVIEW_PACKAGE_RECOVERY.md
host_receipt: episodes/jp_pilot01_hololive_bancho_20260525/review/out08_private_recovery_host_receipt.json
human_review_pending: true
acceptance_granted: false
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
public_or_publishing_acceptance: false
next_action: Thank で exact package を repo 外 ZIP へ export し、私的コピー後に Planner007 で atomic import と server probe を行う。
active_artifact: clip-out08-private-review-package-recovery-v0-001
canonical_main_head: 4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9
canonical_main_baseline: OUT-07 PARK_PROVISIONAL_USABLE parked predecessor
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_08_PRIVATE_REVIEW_PACKAGE_RECOVERY.md, docs/output_layer/out08_private_review_package_recovery_contract.json, docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
durable_context: docs/project-context.md, docs/decision-log.md, docs/idea-ledger.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-08 の二本は Thank (`DESKTOP-H53P1T4`) で exact package として検証済みだが、
`episodes/` 配下の 17-file package は Git に含まれず、Planner007
(`DESKTOP-U9P4LKJ`) には存在しない。現在ホストの probe は
`package_missing` / `server_stopped` であり、localhost URL は current
entrypoint ではない。tracked code、contract、tests、運用ガイドは揃っているので、
状態は build failure ではなく `recovery_kit_ready_package_not_yet_imported` である。

| 維持済み evidence | exact value | ここから変えてはいけないこと |
|---|---|---|
| candidate 01 | SHA-256 `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` | media を再生成・変換しない |
| candidate 02 | SHA-256 `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` | `cut_009` を再導入しない |
| batch manifest | 17 package files、16 payload hashes、self-integrity `22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4` | allowlist 外 file や identity の違う package を受け入れない |
| cut exclusion | `cut_009` reject interval `135.219–144.000`; candidate 02 max source end `135.219` | label や dependent flag で source-time guard を迂回しない |
| source relation | Thank source `6f78657e...103a`; Planner-known source `e2206cef...1889`; byte equivalence not established | Planner sourceから候補を再構築して同一と主張しない |

## 次の三手

1. Thank で `private_export_command` を実行し、利用者が明示した repository 外の
   未作成 ZIP に exact package と sanitized transfer receipt を書く。
2. 利用者が選ぶ private channel で ZIP を一度コピーする。この repository と
   recovery tool は transfer channel の選択、upload、Git transport を行わない。
3. Planner007 で `private_import_command` を実行する。全 archive/package identity
   が通った場合だけ sibling staging を atomic promotion し、local server の HTTP
   200 と MP4 Range 206 を probe する。

PowerShell wrapper を使う場合は次の三つが同じ操作になる。

```powershell
scripts\operator\out08_private_review_package_recovery.ps1 Probe
scripts\operator\out08_private_review_package_recovery.ps1 Export -Destination D:\private-transfer\out08-review.zip
scripts\operator\out08_private_review_package_recovery.ps1 Import -Archive D:\private-transfer\out08-review.zip -StartServer
```

export は last-verified host 名が Thank と一致しなければ停止する。import は unknown
file、欠損、path traversal、backslash、absolute/drive path、duplicate、case
collision、directory、encrypted/link/non-regular entry、CRC failure、hash/size/self
identity mismatch、cut_009 overlap を promotion 前に拒否する。既存 package が invalid
または別 identity なら上書きせず停止し、exact ならそのまま保全する。

## import 後に初めて開く判断

probe が `package_verified_exact` / `server_running_verified` になった後にだけ、
candidate 01 と 02 を一本ずつ direct playback / seek し、テンポ、境界、字幕、
音声の違和感を自由記述で確認する。navigation JPG は移動補助であり thumbnail
candidate ではない。現時点では `human_review_pending=true`、candidate acceptance
も production candidate 化も行っていない。

rights は `pending`。production render、production subtitle design、public、
publishing、upload、OUT-07 thumbnail iteration は閉じたまま。source byte
equivalence も未確立であり、復旧を regeneration に置換しない。

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-08-private-review-package-recovery-v0
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
uvx python -m src.cli.main recover-out08-private-review-package --format json probe
```

expected state は upstream `0 0`、clean worktree、tracked `episodes/` 0。package
がなければ `package_missing` は正常な recovery input であり、code failure ではない。
package が present-invalid の場合は export/import/regeneration を続けず、その category
を報告する。
