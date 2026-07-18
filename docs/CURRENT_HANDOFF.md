---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT09_SECOND_SOURCE_REVIEW_READY
progress_pct: 90
last_touched: 2026-07-18
current_slice: OUT-09
phase: human_review_pending
canonical_status: out08_closed_out09_review_ready
active_branch: codex/out-09-second-source-short-repeatability-v0
verified_implementation_head: branch_head_after_push
source_branch_tip: 29a1a51902bf8140862839e077936b908f775167
closure_branch: null
remote_resume_contract: fetch_then_switch_out09_branch_then_read_this_file
sync_audit_head: 29a1a51902bf8140862839e077936b908f775167
sync_audit_status: out09_branch_push_at_closeout
live_workspace_audit: out09_package_present_manifest_and_video_hashes_match
current_title: OUT-09 second-source Short repeatability human review
human_entrypoint: http://127.0.0.1:8072/index.html
portable_entrypoint: null
review_open_command: powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
decision_required: two_bounded_out09_human_questions
review_status: OUT09_SECOND_SOURCE_SHORT_REPEATABILITY_REVIEW_READY
contract_repair_status: OUT09_INPUT_HASH_RANGE_PROVENANCE_GUARDS_PASSED
remote_code_complete: true
local_artifact_available: true
local_artifact_role: active_same_machine_review_evidence_human_acceptance_pending
portable_local_artifact_available: false
cross_machine_resume_class: tracked_builder_docs_portable_ignored_review_payload_same_machine_only
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: true
acceptance_granted: false
candidate_01_acceptance: pending_human_review
next_action: exact candidate_01について二つの質問だけを回答する
active_artifact: clip-out09-second-source-short-repeatability-v0-001
canonical_main_head: resolve_origin_main_at_resume
canonical_main_baseline: OUT-08 accepted internal closure remains unchanged
source_of_truth: false
owner_lane: output_video_cross_source_repeatability
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
durable_context: docs/project-context.md, docs/idea-ledger.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-09は実装、1回の実render、media/frame/browser QAまで完了し、
`clip-out09-second-source-short-repeatability-v0-001`を人間レビューへ渡せる。
OUT-08 accepted-internal closureは変更していない。現在は`review_ready`であり、
`accepted`ではない。

| 対象 | 実体 | 現在状態 |
|---|---|---|
| source | YouTube `D4i4fjs9PWc`、`【Kroniicle Animation】 Wisdom Teeth Removal Woes` | OUT-08 `7J5aS_pcBj4`と別identity |
| transcript | base Vosk EN + imported YouTube English Original JSON3 | real provider/provenanceあり、human transcript acceptanceなし |
| candidate | source `31.160–58.880s`、semantic `27.720s`、7字幕 | human review pending |
| media | `27.733333s`、H.264/AAC、1080x1920、30fps、yuv420p | full decode/faststart passed |
| exact identity | MP4 `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9` | 人間判断を結ぶhash |
| package integrity | manifest `3f55d16388b1b4197d35ad0e4385e711353932366d8f93ff60ee04500deea692` | self-integrity passed |

## 何を実装したか

`build-second-source-short-repeatability`はsource固有のbranchを持たず、ignored planを
入力にする。planはsource identity、source video/audio material hash、rights/ledger/
Vosk transcript/caption/imported transcript/edit packの6 input hash、allowed/excluded
range、cut/segment linkage、字幕normalization、二つのreview question、closed gatesを
宣言する。

builderはこれらをrender前にfail closedで照合し、OUT-05の共有vertical renderer、
OUT-06のmanifest self-hash、OUT-08のatomic package/navigation/frame QA経路を再利用する。
outputにはMP4、ASS/SRT、4点contact sheet、representative navigation frame、plan、
readback、manifest、single-video HTML、Range server scriptsがある。

## 実証した範囲

| 検証 | 結果 | 意味 |
|---|---|---|
| source/material | video `61c06f75...fd938`、audio `b33b3521...f81b`、ledger一致 | 実acquisition routeとbytesを固定 |
| authority hash | 6/6 verified | planと入力の協調置換を拒否 |
| range | allowed `31.160–58.880s`、excluded overlap 0 | unselected区間をrender前に拒否 |
| transcript linkage | `subtitle_track/youtube_subtitles`、10 linked segments、7 display events | fixtureやVosk誤認識を表示正本にしない |
| render | actual 1、corrective 0、builder 47.413s、外側48.01s | one-pass方針を維持 |
| audio/video | `-14.54 LUFS / -1.48 dBTP`、black/silence event 0 | technical reviewability passed |
| HTTP/browser | page 200、Range 206、readyState 4、seek/resume advance、overflow false、console clean | direct localhost review passed |

## 人間が見るべき二点

次の二問以外へ判断範囲を広げない。

1. 内容とテンポは、1本のShortとして成立していますか？
2. 境界・字幕・音声・映像に違和感はありますか？

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

URLは`http://127.0.0.1:8072/index.html`。serverが止まっていればopen scriptが
`src.cli.serve_review`で再起動する。

## 判断時に隠さない観測

source videoは現行yt-dlpのformat制約により`640x360`で、vertical outputはこれを
1080x1920へreframe/upscaleしたもの。原動画自体に小English captionが焼き込まれて
いるため、下側のOUT-09大字幕と二重表示になる。

さらに`out09_sub_006`はsafe envelope内・3行以下だが、`support`を`suppo / rt`へ
単語途中でwrapする。再生不能、overflow、subtitle containment failureではないが、
question 2の明示的quality debtである。one-pass/no-micro-tuning方針により二回目renderは
行っていない。このexact候補をacceptするか、bounded repairを要求するか、rejectするかを
回答から決める。

## evidence とgateの境界

- `rights=pending`。利用許諾やpublic useを推定しない。
- `production_candidate=false`。production render / subtitle designを受け入れていない。
- thumbnail、metadata、upload、OAuth、visibility、made-for-kids、publishingは未実行。
- packageはignored same-machine evidence。端末間copy/ZIP/importを完了条件にしない。
- YouTube auto-captionはreal provenanceだがhuman transcript acceptanceではない。
- OUT-09一例から3〜5本portfolioや汎用failure rateを結論しない。
- H1へはsource resolution、caption overlap、render elapsed、word split、browser/Range
  readiness、human acceptance pendingをdata-onlyで渡せる。H1自体は実行しない。

## 次に進める入口

| 入口 | 目的 | 次に可能になること | 必要条件 |
|---|---|---|---|
| Verify | exact候補を二問で判断 | accept / bounded repair / rejectへ遷移 | 人間回答 |
| Audit | rolling captionとword wrapをfailure taxonomy化 | source固有tuneと共通ruleを分離 | OUT-09回答 + 追加source evidence |
| Advance | 3〜5本real Shorts portfolioへ進む | cross-source成功率と例外を比較 | OUT-09判断、別source承認 |
| Explore | production limitation-lift packetを設計 | render acceptanceとsubtitle design acceptanceを分離 | portfolio evidence、別ownerのrights判断 |

最短のnext actionは`Verify`。未回答のOUT-09を残したまま別sourceを増やさない。
