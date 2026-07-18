---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT09_STABLE_MANUAL_SAFE_REVIEW_READY
progress_pct: 94
last_touched: 2026-07-19
current_slice: OUT-09
phase: human_review_pending
canonical_status: out09_stable_manual_safe_review_ready
active_branch: codex/out-09-second-source-short-repeatability-v0
verified_implementation_head: branch_head_after_access_safety_push
source_branch_tip: 1ad83c3b37e1867557eef4069393efe13901196b
closure_branch: null
remote_resume_contract: fetch_then_switch_out09_branch_then_read_this_file
sync_audit_head: branch_head_after_access_safety_push
sync_audit_status: out09_access_safety_branch_push_at_closeout
live_workspace_audit: access_only_repair_present_manifest_and_video_hashes_match
current_title: OUT-09 stable manual-safe review access
human_entrypoint: http://127.0.0.1:8072/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Serve -Port 8072
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\serve_preview.ps1 -Port 8072
decision_required: two_bounded_out09_safe_review_questions
review_status: OUT09_STABLE_MANUAL_SAFE_REVIEW_READY
contract_repair_status: OUT09_REVIEW_ACCESS_STABILITY_AND_PLAYBACK_SAFETY_REPAIR_PASSED
user_feedback_overall: unstable_server_and_audible_autoplay_risk_required_access_safety_repair
content_selection_status: not_rejected_not_yet_accepted
subtitle_presentation_timing_status: clear_short_cue_presentation_repaired_pending_review
endpoint_edit_status: unchanged_not_reopened
remote_code_complete: true
local_artifact_available: true
local_artifact_role: active_same_machine_clear_short_cue_review_evidence_human_acceptance_pending
portable_local_artifact_available: false
cross_machine_resume_class: tracked_builder_docs_portable_ignored_review_payload_same_machine_only
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: true
acceptance_granted: false
candidate_01_acceptance: pending_safe_review_exact_sha_human_review
known_unrelated_test_failure: tests/test_vertical_short_candidate.py::test_out06_reviewed_japanese_break_hints_are_measured_and_semantic
known_unrelated_test_failure_2: tests/test_complete_narrative_short.py::test_out06_reviewed_wraps_are_repaired_in_package_readback
known_unrelated_test_failure_scope: unchanged_OUT06_reviewed_wrap_expectations_two_tests_deselected
next_action: foreground serverを維持したclean URLで初期停止・無音とserver継続を確認し、その後に手動再生・音声解除して字幕・終端の違和感だけを回答する
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

OUT-09は、同じartifact ID、`candidate_01`、source `31.160–64.480s`、semantic
`33.320s`、主題、endpoint、27字幕cue、MP4/ASS/SRT byteを維持したまま、レビュー接続だけを
修復した。現在状態は`OUT09_STABLE_MANUAL_SAFE_REVIEW_READY`。operatorが見えるPowerShellで
foreground serverを維持し、clean URLは初期停止・ミュート・音量上限25%となる。技術検証は
通過したが、exact MP4へのhuman acceptanceはまだない。

| 世代 | 画面上の字幕 | 背景canvas | exact MP4 | 判断状態 |
|---|---|---|---|---|
| initial | native caption + 長文burn-in | full-source blur | `300ee360...e0c9` | superseded、acceptanceなし |
| failed repair | 小さいnative captionのみ | full-source blurが字形を複製 | `3e7ef9d8...2916` | 人間が判読性・重複・霜ガラス感を指摘、acceptanceなし |
| current | JSON3由来の短い27 cueをcrisp burn-in | caption-free cropのみ | `b6b90a4b...73da50` | stable manual-safe access、human review pending |

人間観測は従前のAgent/machineによる「native captionは判読可能」という評価を上書きする。
readbackのrepair lineage index 2にはinitialとfailed repairの両SHA、失敗理由
`unreadable_native_caption_and_blurred_caption_duplication`を保持した。

今回さらに、人間が観測した「localhost serverが短時間で消える」「作業中に動画が大きな音で
自動再生された」をpresentation safety defectとして扱った。worker processをserver寿命の
根拠にせず、未知のport ownerを終了したり別portへ逃げたりしない。ブラウザを閉じた際の
Range切断も正常なclient exitとして扱い、server画面へ長い例外を出さない。

## 何を変え、何を維持したか

source `640x360`のcaption-active 10 frameから、native caption bandを
`x=0,y=286,w=640,h=74`と測定した。前景・背景はともにcaption-freeな
`x=0,y=0,w=640,h=286`だけを使う。背景はこのcropを拡大・blurして縦canvasを構成し、
full-source blur fallbackを禁止した。cropが重要内容と衝突した場合のfallbackはneutral
solidまたはcaption-free edgeだけで、今回の10 frameでは衝突なし、maskも不使用だった。

表示字幕はYouTube JSON3のevent開始とtoken offsetを境界authorityとし、27 cueへ分割した。
各cueは1–6語、1–2行、0.48–2.36秒、whole-word wrap。通常は1行で、2行は2 cueだけ。
不透明な黒plateと明瞭なoutline/shadowを使い、blurや半透明frosted surfaceを字幕plateに
使っていない。ASS/SRTは表示とprovenanceの両方を担い、burn-inはtrue、native caption
pixelsはbottom cropで抑止する。

endpoint `64.480s`は再審議していない。last caption `64.360s`、last speech
`64.362812s`の後、次scene直前で閉じる既存authorityを維持し、padding、fade、SFX、
freeze、追加無音は入れていない。

## 成果物と検証値

| 検証面 | 結果 |
|---|---|
| render budget | corrective render 1回、追加render 0、builder `32.904s`、外側`33.498s` |
| media | 5,976,722 bytes、H.264 High/AAC LC、1080x1920、30fps、yuv420p、33.333008s |
| exact identity | `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50` |
| decode/stream | video/audio full decode exit 0、faststart、1 video + 1 audio |
| audio/signal | `-14.80 LUFS / -1.46 dBTP`、blackdetect 0、silencedetect 0 |
| manifest | self `50ff14e5ee9ffae0ab1cb31f33a584c346026d7674c360546302e10de24e62ff`、10 package files一致 |
| plan | input SHA `569ba9d193348d76ee368dde32ebd7c00c485a03792b4728562efec452b00c7e`、package snapshot一致 |
| frame QA | 10点contactでnative caption、blurred glyph duplicate、frosted subtitle surfaceなし。顔・主動作・最後の`So.`を確認 |
| server | foreground PowerShellで3 probeを54秒超にわたり通過、page 200、Range 206、close/reopen継続、正しい二重起動は再利用、未知port ownerは終了せず拒否、Ctrl+C後listener 0 |
| browser | clean URLは2.1秒後もpaused/muted/currentTime 0、手動Spaceで再生進行、close/reopenで同じ初期状態。QA exact queryだけがmuted再生後pause、console warn/error 0 |
| responsive | default幅と375px級でhorizontal overflow false、質問2件、動画errorなし |
| tests | review server / OUT-09 targeted tests passed。RuffとPowerShell parseもpassed |

既知のOUT-06 reviewed-wrap debtは今回のaccess-only契約外で、full suiteや媒体renderは
再実行していない。shared rendererの既定filter文字列は従来どおりで、caption-free
compositionは明示policyを渡したOUT-09にだけ適用する。

## 開く場所と人間が答える二問

正本はforeground server commandである。次を人間が見えるPowerShellで実行し、その窓を
レビュー中は開いたままにする。停止は`Ctrl+C`で行う。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\serve_preview.ps1 -Port 8072
```

health確認後にclean URL `http://127.0.0.1:8072/index.html`を開く。server起動とURL openを
一度に行う便宜routeは次で、別の見えるPowerShellにforeground serverを起動する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Serve -Port 8072
```

`open_preview.ps1`を`-Serve`なしで実行した場合、healthy serverがあればclean URLだけを開き、
なければ正本commandを表示して終了する。暗黙起動、QA query付与、未知processの終了はしない。
質問は次の二つだけである。

1. ページを開いた直後に動画や音が勝手に始まらず、レビュー中にserverが維持されるか。
2. 手動で再生・音声解除した後、字幕の切替・可読性・終わり方に明確な違和感があるか。

回答はcurrent exact MP4 SHAだけへ結び付ける。initial/failed predecessorへ遡及せず、
production、rights、thumbnail、public/publishing、portabilityを同時に承認しない。

## 閉じたgateと次の距離

- `episodes/`はignoredのままで、`git ls-files episodes`は0。packageは同一マシン証跡である。
- human transcript acceptance、production subtitle design/render、640x360 sourceのproduction
  画質、rights/material use、thumbnail、public/publishing/uploadは未承認。
- OUT-08以前の成果物は変更していない。OUT-09の技術修復からsuccessor acceptanceや
  3–5本portfolioの一般則を推論しない。
- 直近は上の二問を回収してOUT-09をaccept / reframe / rejectのいずれかへ遷移する。
  accept後の最も遠い安全な目標は、異なる3–5 sourceでcaption-free detection、cue
  segmentation、重要内容crop conflict、production limitationを比較し、source-specific
  ruleと共有可能ruleを分離したportfolio evidence packetを作ること。rights/public gateは
  その後も別ownerの判断として残す。
