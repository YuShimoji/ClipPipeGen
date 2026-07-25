---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_M6_RIGHTS_PACKET_READY_FOR_HUMAN_DECISION_V1
last_touched: 2026-07-25
current_slice: OUT-13
phase: rights_decision_readiness
canonical_status: m6_packet_prepared_rights_decision_pending
active_branch: codex/m6-rights-decision-readiness-v1
source_branch: codex/out-13-editorial-video-candidate-v1
development_baseline_main_revision: 5bd6e65318df129bebc87291c2ae733f143ed8d8
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
accepted_feature_revision: 18641fe917b084259869263e8db05d78325aa2db
integrated_main_revision: 18641fe917b084259869263e8db05d78325aa2db
integration_method: fast_forward_no_squash_no_history_rewrite
integration_authority_id: clip-out13-main-integration-authorization-20260725-01
integration_authority_consumed: true
final_main_revision_locator: refs/heads/main
m5_verification_tree_locator: refs/heads/main^{tree}
remote_resume_contract: fetch_then_switch_main_then_read_this_file
current_title: OUT-13 M6 rights decision packet is ready; human owner verdict is pending
human_entrypoint: docs/rights/out13_m6_rights_decision_readiness_packet.json
portable_entrypoint: docs/rights/out13_m6_rights_decision_readiness_packet.json
review_open_command: powershell -NoProfile -Command Invoke-Item docs\rights\out13_m6_rights_decision_readiness_packet.json
review_server_restart_command: null
machine_readback: docs/rights/out13_m6_rights_decision_readiness_packet.json
decision_required: human_rights_owner_allow_deny_or_restrict
review_status: rights_decision_packet_ready_owner_verdict_pending
remote_code_complete: true
local_artifact_available: true
local_artifact_role: accepted_exact_candidate_005_same_machine_evidence
portable_local_artifact_available: false
cross_machine_resume_class: tracked_m6_packet_acceptance_receipt_and_code_are_portable_private_media_and_generated_package_are_not
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
main_integration_approved: true
main_integration_preflight_verdict: consumed_by_authorized_fast_forward_integration
main_integration_approval_consumed_by_revision: 18641fe917b084259869263e8db05d78325aa2db
m4_main_integration_status: complete
m5_integrated_baseline_verification_status: passed
m6_rights_status: packet_prepared_rights_decision_pending
m6_packet_status: READY_FOR_HUMAN_RIGHTS_DECISION
m6_packet: docs/rights/out13_m6_rights_decision_readiness_packet.json
next_review_due: human_rights_owner_decision
next_review_type: human_rights_owner_decision
pause_reason: human_rights_owner_verdict_and_authority_evidence_pending
next_action: obtain_human_rights_owner_verdict_for_exact_m6_packet_without_starting_production_or_public_work
active_artifact: clip-out13-editorial-video-candidate-v1-005
source_of_truth: true
owner_lane: rights_readiness_handoff
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/rights/out13_m6_rights_decision_readiness_packet.json, docs/RUNTIME_HISTORY.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, docs/output_layer/out13_human_acceptance_receipt.json, artifacts/ARTIFACTS.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## M6判断準備パケット作成済み、human owner verdict待ち

OUT-13のaccepted feature revision
`18641fe917b084259869263e8db05d78325aa2db`は、start main
`5d6f69a64d510508a1f78ab3111a7780913a019c`の直系15 commitとして、
authority `clip-out13-main-integration-authorization-20260725-01`に基づき
`main`へfast-forward統合された。squash、merge commit、force、履歴改変はない。
accepted feature commitはfinal mainの祖先で、統合直後のtreeはaccepted feature treeと同一だった。

M5はfinal closure treeを対象に、configured full Python suite、focused OUT-13 /
acceptance dedup / current resume authority / active state / dashboard、dashboard再生成、
compile/static、diff/privacy境界を検証してpassした。final main commitのexact SHAは
自己参照するtracked文書へ埋め込まず、push後の`refs/heads/main`をGit正本として解決する。

今回の開発基準はmain revision
`5bd6e65318df129bebc87291c2ae733f143ed8d8`。そこから
`codex/m6-rights-decision-readiness-v1`を作り、M6 packet
`docs/rights/out13_m6_rights_decision_readiness_packet.json`を追跡可能な判断面として
準備した。packet statusは`READY_FOR_HUMAN_RIGHTS_DECISION`であり、rights approved
という意味ではない。

## M2受領はそのまま継承

accepted artifactは`clip-out13-editorial-video-candidate-v1-005`、exact final MP4 SHAは
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`、
review contextは
`out13_candidate_005_internal_full_view_editorial_visual_review_v1`である。
構成、編集フロー、字幕提示、内部用途の画質・音質というaccepted dimensionsは変更していない。
`human_review_pending=false`を維持し、同じmedia/context/dimensionsへ再reviewを作らない。

受領時点のreceipt内`main_integration_approved=false`は、M2がmain承認を含まなかったという
historical factとして変更しない。今回のmain承認と消費記録はRuntime/Handoff/監修報告へ分離し、
artifact受領scopeを広げない。

## Artifactとportable境界

| 対象 | 現在の役割 | Git portability |
|---|---|---|
| acceptance receipt | M2のexact identityと判断scope | portable |
| main code/docs/tests | M4/M5 integrated baseline | portable |
| M6 rights packet | material/range/terms/unknowns と owner decision fields | portable |
| Candidate 003–005 package/media | same-machine retained evidence | non-portable |
| rights owner verdict / production / public receipts | 未作成・未承認 | not started |

`episodes/`はignoredかつtracked 0件を維持する。Candidate 003–005のplan、caption、
manifest、image、audio、MP4は変更しない。private mediaがGit cloneへ移らないことは
既知のboundaryであり、M5 failureではない。

## M6 packetが判断可能にした範囲

| 判断対象 | packetへ固定した内容 | 現在の不足 | ownerの次の動き |
|---|---|---|---|
| source visual | source SHA、7使用range、限定contact-sheet観察 | 全rangeの第三者要素確認 | 各rangeのcharacter、logo、artwork等を観察しverdictへ反映 |
| source audio | 同じ7rangeのAAC音声、技術lineage | music、voice、performanceの権利分類 | 全rangeを聴取し別条件の要否を記録 |
| provider caption | exact JSON3 SHA、102 cue、burn-in利用 | caption text再製のpermission basis | allow/deny/restrictionとattributionを決める |
| Keifont | finalに使ったexact font SHA、一次配布条件 | exact bytesとlicense/NOTICEのbinding | 証跡locatorを追加するか新identityでfontを変更 |
| generated layers | 7 cut、字幕layout、outline/shadow、review metadata | project-authored representation | underlying素材と分離してowner確認 |
| source-embedded elements | character likeness、source-native text/graphicを限定観察 | music、guest voice、logo、displayed workの全編確認 | range別content observationを完了 |

使用propositionは、accepted 128.833333秒MP4をYouTubeでpublic、worldwide、
monetization contemplatedとして扱う保守的な単一案である。source URL/titleをdescription
先頭へ置き、Content ID登録はせず、thumbnail reuseは今回の判断外とした。publisher/channelの
法的identity、channel registration、visibility、territory、duration、判断者authorityは未入力である。

技術provenance、限定content observation、一次規約、permission / owner authority、
内部editorial受領、platform policyを別classにした。sourceがpublic、hashが一致、
captionをanonymous取得できた、M2で映像がacceptedという事実は、いずれもpermissionを
意味しない。

## 独立した未承認gate

- rights approval: `pending`
- M6 packet readiness: `READY_FOR_HUMAN_RIGHTS_DECISION`
- owner verdict: `undecided`
- owner identity / authority evidence: 未記録
- full seven-range rights content observation: 未完了
- provider caption permission basis: 未記録
- exact Keifont distribution/license binding: 未記録
- production subtitle/design/render acceptance: `false`
- production image quality acceptance: `false`
- thumbnail acceptance: `false`
- publishing / upload / public release: 未承認・未実行
- credentials / OAuth / visibility / deployment: 未承認・未実行

## Next Action

次の一手は
`obtain_human_rights_owner_verdict_for_exact_m6_packet_without_starting_production_or_public_work`。
Rights owner / User はpacketの単一intended-use proposition、8 material rows、7 range rows、
一次規約、局所化済み不足を読み、判断者identityとauthority evidenceを結び付ける。
全体または列挙対象ごとに`allow` / `deny` / `allow_with_restrictions`を記録し、制限、
attribution、decision date、receipt locatorを固定するまではM6をclosedにしない。

packet確認:

```powershell
Invoke-Item docs\rights\out13_m6_rights_decision_readiness_packet.json
```

## mainからの再開

```powershell
git fetch --prune origin
git switch codex/m6-rights-decision-readiness-v1
git pull --ff-only origin codex/m6-rights-decision-readiness-v1
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
git merge-base --is-ancestor 5bd6e65318df129bebc87291c2ae733f143ed8d8 HEAD
git merge-base --is-ancestor 18641fe917b084259869263e8db05d78325aa2db HEAD
git ls-files episodes
```

remote feature branch作成後の期待値はfeature/upstream parity `0 0`、start main
`5bd6e65318df129bebc87291c2ae733f143ed8d8`とaccepted featureのancestry pass、
tracked `episodes/` 0件、tracked worktree cleanである。feature branchがlocalにない
fresh cloneでは、fetch後に`git switch --track origin/codex/m6-rights-decision-readiness-v1`
で作成する。
