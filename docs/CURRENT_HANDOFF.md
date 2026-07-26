---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT14_PUSH_MICROARC_REAL_STREAM_READY_FOR_HUMAN_REVIEW
last_touched: 2026-07-26
current_slice: OUT-14
phase: exact_artifact_human_review_pending
canonical_status: out14_push_microarc_real_stream_ready_for_human_review
active_branch: codex/out14-push-microarc-real-stream-v1
source_branch: origin/main
development_baseline_main_revision: edb782acd1e06aca46e0a5d10295ea52f30ad5c7
base_head: edb782acd1e06aca46e0a5d10295ea52f30ad5c7
accepted_feature_revision: null
integrated_main_revision: null
integration_method: not_started
integration_authority_id: null
integration_authority_consumed: false
final_main_revision_locator: refs/heads/codex/out14-push-microarc-real-stream-v1
m6_decision_binding_revision: 097fcaad8985d4f24077da484819efb5942b9c65
m6_decision_main_integration_authority_id: clip-m6-deny-main-integration-20260726-01
m6_decision_main_integration_authority_consumed: true
m6_decision_binding_remote_ref: refs/heads/main
m5_verification_tree_locator: refs/heads/main^{tree}
remote_resume_contract: fetch_then_switch_branch_then_read_this_file
current_title: OUT-14 Push Micro-Arc real stream package ready for exact-artifact human review
human_entrypoint: episodes/out14_push_microarc_real_stream_20260726/artifacts/clip-out14-push-microarc-stream-v1-001/review/index.html
portable_entrypoint: docs/output_layer/OUT_14_PUSH_MICROARC_REAL_STREAM.md
review_open_command: powershell -NoProfile -File episodes\out14_push_microarc_real_stream_20260726\artifacts\clip-out14-push-microarc-stream-v1-001\review\open_preview.ps1
review_server_restart_command: uvx python -m src.cli.serve_review --root episodes/out14_push_microarc_real_stream_20260726/artifacts/clip-out14-push-microarc-stream-v1-001 --port 8078
machine_readback: episodes/out14_push_microarc_real_stream_20260726/artifacts/clip-out14-push-microarc-stream-v1-001/run_manifest.json
decision_required: exact_out14_artifact_internal_editorial_visual_language_verdict
review_status: ready_for_human_review
remote_code_complete: false
remote_decision_binding_available: false
local_decision_binding_committed: false
remote_mutation_authorized: false
local_artifact_available: true
local_artifact_role: exact_internal_human_review_target
portable_local_artifact_available: false
cross_machine_resume_class: tracked_out14_code_and_docs_are_portable_ignored_source_receipts_plan_and_package_are_not
rights_approval: not_granted
public_use_verdict: not_evaluated_for_out14
monetized_youtube_verdict: not_evaluated_for_out14
publication_decision: not_authorized
monetization_decision: not_evaluated
m6_owner_verdict: deny
m6_decision_evidence_locator: docs/rights/out13_m6_rights_decision_readiness_packet.json#/decision_history/0
m6_starting_packet_revision: dac5f7fb715cb3a7acd6c982a80cb916492e7880
candidate_public_default: off
candidate_excluded_from_production_publish_upload_release_sets: true
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: true
automation_acceptance_granted: true
automation_acceptance_scope: out14_builder_exact_source_plan_caption_receipts_render_validation_resume_and_http_readback
editorial_acceptance_granted: false
acceptance_receipt: null
acceptance_review_context_id: out14_push_microarc_exact_media_full_view_editorial_visual_language_review_v1
acceptance_media_sha256: 1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f
acceptance_dimensions: pending_editorial_composition, pending_boundary_naturalness, pending_subtitle_language_accuracy, pending_picture_and_audio_internal_use
same_review_identity_reopens_human_review: false
bounded_repair_reopens_only_affected_dimensions_and_timestamps: true
main_integration_approved: false
main_integration_preflight_verdict: not_started
main_integration_approval_consumed_by_revision: null
m4_main_integration_status: not_applicable_out14
m5_integrated_baseline_verification_status: not_applicable_out14
m6_rights_status: closed_deny_exact_artifact
m6_packet_status: M6_CLOSED_DENY_EXACT_ARTIFACT
m6_packet: docs/rights/out13_m6_rights_decision_readiness_packet.json
next_review_due: now
next_review_type: exact_out14_full_view_editorial_visual_language_review
pause_reason: null
next_action: open_exact_out14_review_and_record_accept_bounded_repair_or_reject_without_expanding_rights_or_publication_scope
active_artifact: clip-out14-push-microarc-stream-v1-001
source_of_truth: true
owner_lane: human_editorial_visual_language_review
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_14_PUSH_MICROARC_REAL_STREAM.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, docs/rights/out13_m6_rights_decision_readiness_packet.json, artifacts/ARTIFACTS.md
upstream_parity: 0 1
---

# Current Handoff - ClipPipeGen

## OUT-14 は exact artifact の human review 待ち

remote `origin/main` exact revision
`edb782acd1e06aca46e0a5d10295ea52f30ad5c7`から隔離 branch
`codex/out14-push-microarc-real-stream-v1`を作り、active worktreeを変更せずに
`clip-out14-push-microarc-stream-v1-001`を生成した。tracked implementation と docs は
この branch の単一 local commitに閉じ、push、PR、merge、main integration、upload、
publication、visibility changeは行わない。

source は `youtube:rltNvZ_FY8Q`、大空スバルの公開済み free-talk archive。
4848.047891秒の source から 786.36–1487.52秒を一つの連続 range として採用し、
701.166667秒の H.264/AAC 1920x1080 MP4を作った。映像 SHAは
`1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f`。
取得 source は640x360で、出力はLanczos upscaleである。native 1080pとは扱わない。

plan は `PUSH_MICROARC` profile、1 media cut、2 intentional omitted ranges、
hook / context / development / payoff / aftermath の5役割、provider自動字幕178 cue、
creator context 0件を持つ。字幕はselection evidenceで、逐語 transcript、
公式著者字幕、話者同定ではない。

full decode、faststart、timestamp、A/V sync、mapping 1.0、-15.0 LUFS、
black/silence 0、caption containment、manifest閉集合がpassした。同一入力resumeは
2.822秒で再レンダーせずpass。localhostはreview page 200、MP4 Range 206。
代表フレームでは文字切れや二重表示は見つからなかったが、0.834秒cueの
「猿み」のような自動字幕由来の不自然な分割があり、言語校正はhuman gateである。

次の一手は exact SHA の全編を開き、`accept / bounded_repair / reject`の一つを
内部editorial/visual/language scopeへbindすること。acceptでもrights、production、
YPP、thumbnail、Shorts、upload、publicationは開かない。bounded repairなら変更した
timestamp/caption/layoutだけを新review identityにする。

## 過去の OUT-13 M6 closed deny

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

deny-binding revision
`097fcaad8985d4f24077da484819efb5942b9c65`はauthority
`clip-m6-deny-main-integration-20260726-01`によりcanonical `main`へ通常fast-forwardされ、
remoteへpush済みである。再開branchは`main`、live canonical tipは`refs/heads/main`、
remote decision bindingはavailable、upstream parityは`0 0`である。

今回の開発基準はmain revision
`5bd6e65318df129bebc87291c2ae733f143ed8d8`。そこから
`codex/m6-rights-decision-readiness-v1`を作り、M6 packet
`docs/rights/out13_m6_rights_decision_readiness_packet.json`を追跡可能な判断面として
準備した。開始packet revision
`dac5f7fb715cb3a7acd6c982a80cb916492e7880`は
`READY_FOR_HUMAN_RIGHTS_DECISION`だった。

ユーザーは監修役の推奨1「deny — exact MP4の収益公開は行わず、後継版へ移る」を選択した。
この判断をCandidate
`clip-out13-editorial-video-candidate-v1-005`とexact MP4 SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`
へbindした。現在のpacket statusは`M6_CLOSED_DENY_EXACT_ARTIFACT`、
`public_use_verdict=deny`、`monetized_youtube_verdict=deny`、
`rights_approval=not_granted`である。

denyの主体はproject publication decision ownerとしてのユーザーである。underlying source
rightsholderとは表明せず、infringement等の法的結論、source / caption / font /
source-embedded elements一般への判断、future artifactへのdenyには拡張しない。

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
| M6 rights packet | exact deny event、material/range/terms/unknowns | portable |
| Candidate 005 package/media | read-only internal evidence、public default off | non-portable |
| production / publish / upload / release candidate role | Candidate 005を除外 | closed for exact artifact |

`episodes/`はignoredかつtracked 0件を維持する。Candidate 003–005のplan、caption、
manifest、image、audio、MP4は変更しない。private mediaがGit cloneへ移らないことは
既知のboundaryであり、M5 failureではない。

## M6 deny後も保持する未解決証拠

| 判断対象 | packetへ固定した内容 | 現在の不足 | deny後の扱い |
|---|---|---|---|
| source visual | source SHA、7使用range、限定contact-sheet観察 | 全rangeの第三者要素確認 | 未解決のまま保存。exact public path closureにはnonblocking |
| source audio | 同じ7rangeのAAC音声、技術lineage | music、voice、performanceの権利分類 | 未解決のまま保存。permissionへ昇格させない |
| provider caption | exact JSON3 SHA、102 cue、burn-in利用 | caption text再製のpermission basis | 未解決のまま保存 |
| Keifont | finalに使ったexact font SHA、一次配布条件 | exact bytesとlicense/NOTICEのbinding | 未解決のまま保存 |
| generated layers | 7 cut、字幕layout、outline/shadow、review metadata | project-authored representation | underlying素材と分離した証拠として保存 |
| source-embedded elements | character likeness、source-native text/graphicを限定観察 | music、guest voice、logo、displayed workの全編確認 | 未解決のまま保存 |

使用propositionは、accepted 128.833333秒MP4をYouTubeでpublic、worldwide、
monetization contemplatedとして扱う保守的な単一案である。source URL/titleをdescription
先頭へ置き、Content ID登録はせず、thumbnail reuseは今回の判断外とした。publisher/channelの
法的identity、channel registration、visibility、territory、duration、判断者authorityは未入力である。

技術provenance、限定content observation、一次規約、permission / owner authority、
内部editorial受領、platform policyを別classにした。sourceがpublic、hashが一致、
captionをanonymous取得できた、M2で映像がacceptedという事実は、いずれもpermissionを
意味しない。

## closed stateと独立gate

- rights approval: `not_granted`
- M6 state: `M6_CLOSED_DENY_EXACT_ARTIFACT`
- exact artifact public-use verdict: `deny`
- exact artifact monetized-YouTube verdict: `deny`
- project publication decision evidence: packet `decision_history/0`
- underlying rightsholder identity / permission authority: 未記録
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
`require_materially_distinct_successor_artifact_before_any_new_public_or_monetized_consideration`。
新しいpublic / monetized considerationを開く場合は、Candidate 005を変更せず、
materially distinctなsuccessor scopeを先にユーザーが決める。新artifact identity、新しい
transformation / content strategy、material / range inventory、editorial review、
rights reviewが必要である。このMissionではsuccessorの作成、設計、spec、renderを開始しない。

packet確認:

```powershell
Invoke-Item docs\rights\out13_m6_rights_decision_readiness_packet.json
```

## mainからの再開

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
git merge-base --is-ancestor 097fcaad8985d4f24077da484819efb5942b9c65 HEAD
git merge-base --is-ancestor 5bd6e65318df129bebc87291c2ae733f143ed8d8 HEAD
git merge-base --is-ancestor 18641fe917b084259869263e8db05d78325aa2db HEAD
git ls-files episodes
```

期待値はmain/upstream parity `0 0`、deny-binding revision
`097fcaad8985d4f24077da484819efb5942b9c65`、start main
`5bd6e65318df129bebc87291c2ae733f143ed8d8`、accepted feature
`18641fe917b084259869263e8db05d78325aa2db`のancestry pass、tracked `episodes/` 0件、
tracked worktree cleanである。old M6 feature branchはhistorical evidenceであり、
current resumption targetには使わない。
