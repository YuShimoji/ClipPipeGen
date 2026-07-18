---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT09_REPAIRED_REVIEW_READY
progress_pct: 92
last_touched: 2026-07-18
current_slice: OUT-09
phase: human_review_pending
canonical_status: out09_bounded_repair_review_ready
active_branch: codex/out-09-second-source-short-repeatability-v0
verified_implementation_head: branch_head_after_repair_push
source_branch_tip: 0177629021e5926e989cdce0c86f2d42e20bbfc8
closure_branch: null
remote_resume_contract: fetch_then_switch_out09_branch_then_read_this_file
sync_audit_head: 0177629021e5926e989cdce0c86f2d42e20bbfc8
sync_audit_status: out09_repair_branch_push_at_closeout
live_workspace_audit: repaired_out09_package_present_manifest_and_video_hashes_match
current_title: OUT-09 native-caption and endpoint bounded repair review
human_entrypoint: http://127.0.0.1:8072/index.html
portable_entrypoint: null
review_open_command: powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
decision_required: one_bounded_out09_repair_question
review_status: OUT09_SUBTITLE_AUTHORITY_AND_ENDPOINT_REPAIRED_REVIEW_READY
contract_repair_status: OUT09_NATIVE_CAPTION_AND_ENDPOINT_REPAIR_PASSED
user_feedback_overall: bounded_repair_required
content_selection_status: not_rejected_not_yet_accepted
subtitle_presentation_timing_status: needs_adjustment_addressed_pending_review
endpoint_edit_status: needs_adjustment_addressed_pending_review
remote_code_complete: true
local_artifact_available: true
local_artifact_role: active_same_machine_repaired_review_evidence_human_acceptance_pending
portable_local_artifact_available: false
cross_machine_resume_class: tracked_builder_docs_portable_ignored_review_payload_same_machine_only
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: true
acceptance_granted: false
candidate_01_acceptance: pending_repaired_exact_sha_human_review
known_unrelated_test_failure: tests/test_vertical_short_candidate.py::test_out06_reviewed_japanese_break_hints_are_measured_and_semantic
known_unrelated_test_failure_scope: unchanged_OUT06_Japanese_line_measurement_expected_3_lines_observed_2
next_action: 修復後candidate_01について字幕の切替リズムと終わり方が自然かを一問だけ回答する
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

OUT-09の同じsource・主題・開始点・artifact IDを維持し、ユーザー指摘の字幕authorityと
終端だけを1回のbounded repairで修復した。現在は
`OUT09_SUBTITLE_AUTHORITY_AND_ENDPOINT_REPAIRED_REVIEW_READY`で、human acceptanceは
まだpendingである。

| 対象 | 修復前 | 修復後 |
|---|---|---|
| subtitle authority | source-native caption + ClipPipeGen長文burn-in | source-native caption pixelsのみ。追加burn-in 0 |
| sidecar | 7 ASS/SRT eventを表示にも使用 | 9 ASS/SRT eventをprovenance/navigation/readback専用で保持 |
| endpoint | `58.880s`、caption `Man,`と発話途中 | `64.480s`、caption/発話完了後・次scene直前 |
| semantic/media duration | `27.720 / 27.733333s` | `33.320 / 33.333333s` |
| MP4 SHA-256 | `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9` | `3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916` |

旧SHAはsuperseded predecessorとしてreadbackへ保持し、acceptanceは主張しない。新しい
人間判断は新SHAだけへ結び付ける。

## 修復根拠

- 最後のsource-native captionは`64.360s`で完結。
- 最後の発話は`64.362812s`で終わり、`64.541125s`まで短い無音がある。
- 次sceneと次native captionは`64.480s`から始まる。
- end-exclusive `64.480s`を採用し、固定padding、fade、SFX、freeze、追加無音は不使用。
- 1080x1920 frameと216x384相当frame、375px browser viewportでnative captionを判読。

## 実装と検証

builderはignored planのuser feedback、predecessor SHA、native-caption-only mode、自然終端
evidenceをrender前に検証する。表示用ASSではなくDialogue 0件のinternal carrierを共有
OUT-05 render pathへ渡すため、packageのASS/SRTは維持しつつ動画pixelへ追加字幕を
書き込まない。

| 検証 | 結果 |
|---|---|
| render | corrective 1回、追加repair 0、builder `31.729s`、外側`32.276s` |
| media | H.264/AAC、1080x1920、30fps、33.333333s、full decode/faststart passed |
| audio/signal | `-14.80 LUFS / -1.46 dBTP`、black/silence event 0 |
| manifest | self-integrity `440c73dde6b33e9ba9ce63a512e61f5974e947032a507ac17c560d560a028078`、10 package files / 6 inputs一致 |
| HTTP/browser | 200/Range 206、readyState 4、error null、seek/resume、desktop/mobile overflow false、console clean |
| targeted tests | OUT-09と直接影響・現状面は`41 passed, 2 skipped, 1 deselected`。今回未変更のOUT-06日本語改行測定1件は単独でもfail |

除外したOUT-06テストは、期待する3行に対して現行測定が2行を返す既存経路の監査事項で、
今回のOUT-09実装ファイルには差分がない。OUT-09のacceptanceを偽って広げず、別のOUT-06
regression auditで原因を確定する。

## 人間が確認する一問

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

URLは`http://127.0.0.1:8072/index.html`。

> 字幕の切替リズムと終わり方が自然になったか、ほかに明確な違和感があれば教えてください。

## Evidenceとgate

- user feedbackは`bounded_repair_required`。content selectionはreject/acceptのどちらでもない。
- native-caption-onlyはこのsource固有modeで、production subtitle policyへ一般化しない。
- sourceは640x360取得物のreframeで、production画質acceptanceではない。
- rights、production、thumbnail、public/publishing、upload/OAuthは閉じたまま。
- ignored packageはsame-machine evidenceで、portabilityを主張しない。
- H1へはbefore/after SHA、caption authority、endpoint timing、repair elapsed、browser/mobile
  readiness、human acceptance pendingをdata-onlyで渡す。H1自体は実行しない。

## 次に進める入口

| 入口 | 次の動き | 必要条件 |
|---|---|---|
| Verify | 新SHAへ一問の回答を結びaccept / reframe / rejectを確定 | 人間回答 |
| Audit | native-caption-onlyの成功条件をsource固有dataとして記録 | OUT-09 closure |
| Advance | 3〜5本portfolioでsource横断規則を比較 | OUT-09 closure、別source承認 |

最短のnext actionは`Verify`であり、この回答前に別variantや追加renderを作らない。
