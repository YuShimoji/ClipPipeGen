---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_LOCAL_EXACT_REVIEW_READY_HUMAN_EDITORIAL_DECISION_PENDING_V1
progress_pct: 97
last_touched: 2026-07-25
current_slice: OUT-13
phase: human_editorial_review_pending
canonical_status: remote_contract_green_local_exact_review_ready
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
sync_baseline_head: 396432635710622f6573ae15e3f0537452a6c14f
verified_implementation_head: this_commit_after_push
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 tracked implementation and exact candidate 005 are locally review-ready; human editorial verdict is pending
human_entrypoint: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v005/review/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\serve_preview.ps1 -Port 8076
machine_readback: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v005/validation_readback.json
decision_required: human_editorial_accept_bounded_repair_or_reject_for_exact_candidate_005_sha
review_status: machine_and_http_validated_human_editorial_review_pending
remote_code_complete: true
local_artifact_available: true
local_artifact_role: active_exact_candidate_005_same_machine_review_target
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_portable_exact_inputs_plan_and_output_are_same_machine_only_and_require_private_transfer_or_new_identity_build_elsewhere
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: true
automation_acceptance_granted: true
automation_acceptance_scope: tracked_builder_plus_current_host_exact_resume_package_hash_and_http_readback
editorial_acceptance_granted: false
next_action: open_exact_candidate_005_then_bind_accept_bounded_repair_or_reject_to_final_sha
active_artifact: clip-out13-editorial-video-candidate-v1-005
remote_handoff_tip: this_commit_after_push
source_of_truth: true
owner_lane: editorial_real_video_internal_review
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, artifacts/ARTIFACTS.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

2026-07-25 JSTにactive branch
`codex/out-13-editorial-video-candidate-v1`をremote tip
`396432635710622f6573ae15e3f0537452a6c14f`へff-only更新した。開始時はlocal
`673da5d`に対してremoteが2 commit先行していた。取り込み後のupstream parityは`0 0`、
`origin/main...HEAD`は`0 12`、`origin/main`はHEADの祖先である。OUT-13側12 commitは
main未統合であり、このhandoff更新commitをpushした後は`0 13`になる。

remote最新文書はcandidate 005を「current checkoutに不在」としていたが、current rootの
ignored `episodes/`にはexact plan / inputs / 25-file package / MP4 / validation / launcherが
存在した。live SHA、package-tree digest、`--resume`、HTTPを再測定し、source-host receiptと
current local artifactを同一identityとして照合できたため、現在の停止点をartifact recoveryから
human editorial reviewへ戻した。

Node依存は`npm ci`で再構成し、`npm ls --depth=0`、GUI / Electron smoke、OUT-13 CLI helpを
確認した。Python full suiteは654 passed in 94.36s、post-dashboard current-state testsは
30 passedで、tracked regressionはgreen。

## exact candidate 005のlive readback

| 対象 | live結果 | workflow上の意味 |
|---|---|---|
| source | 35,281,366 bytes、SHA `6f78657e...103a` | candidate 005 contractと一致 |
| transcript | 43,369 bytes、SHA `4a7b4fd8...3495` | contractと一致 |
| provider JSON3 | 40,303 bytes、SHA `3c15535f...9919` | contractと一致 |
| rights snapshot | 2,347 bytes、SHA `4302c4a1...7bb8` | bytesは一致、rights statusはpending |
| plan | 11,260 bytes、SHA `27ef1aa9...dac2` | candidate 005 identityを再現可能 |
| package | 25 files / 87,123,995 bytes | ignored same-machine evidence |
| final MP4 | 82,594,810 bytes、128.833333s、SHA `a76babda...bbb5` | human verdictをbindするexact target |
| package-tree digest | `ed45fd4c...040` | tracked contract、resume前後と一致 |
| exact resume | 9.173s、renderなし、5 cache hits | 成功package不変、sibling journalだけ更新 |
| review server smoke | page 200、MP4 Range 206 | launcher経路利用可能。検証後server停止 |

packageの`visual_observation.status`は`unverified`で、人間の全編視聴結果はまだない。
machine validation、decode、hash、HTTPはeditorial acceptanceの代用にならない。

## 次に実行する一手

同一マシンで次を実行し、candidate 005を全編視聴する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
```

人間はfinal SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`へ
`accept` / `bounded repair` / `reject`のいずれかをbindする。repairの場合はfindingを
cut ID・caption ID・timestampへ限定し、candidate 006以降のnew identityを割り当てる。
candidate 004 / 005は上書きしない。

editorial closure後にbranch acceptanceとmain integration preflightへ進む。rights、
production subtitle/design/render、thumbnail、publishing、upload、public releaseは
独立gateであり、このmachine greenから開かない。

## portableな実装とportableでない証拠

| 対象 | Git cloneで移るか | 別端末での扱い |
|---|---|---|
| code / tests / docs / exact contract | 移る | branchをff-only同期してvalidation |
| candidate identity / expected SHA群 | 移る | current packageとlive照合 |
| source / transcript / plan / MP4 / QA images | 移らない | 承認済みprivate transfer + 全hash照合、またはnew identity rebuild |
| review launcher path | 文書上は移るが対象bytesは移らない | `Test-Path`とhash成功後だけ利用可能と報告 |

`git ls-files episodes`は空を維持する。protected R3 preview sessionを含む`episodes/`へ
broad ignored cleanupを実行しない。

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count HEAD...origin/codex/out-13-editorial-video-candidate-v1
git ls-files episodes
```

期待値はbranch parity `0 0`、tracked `episodes/` 0件。続いて
`docs/SUPERVISOR_STATUS_REPORT.md`を読み、candidate pathとinput/package SHAをlive再判定する。
このホストの`local_artifact_available=true`を別hostへ自動継承しない。
