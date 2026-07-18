---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT09_ACCEPTED_INTERNAL_CANONICAL_MAIN
progress_pct: 100
last_touched: 2026-07-19
current_slice: OUT-09
phase: accepted_internal_canonical_main
canonical_status: out09_accepted_internal_canonical_main
active_branch: main
verified_implementation_head: branch_head_after_acceptance_closure_push
source_branch_tip: 17436ad482f5e10db12b1461ec3caee18ae932d3
closure_branch: main
remote_resume_contract: fetch_then_switch_main_then_read_this_file
sync_audit_head: branch_head_after_acceptance_closure_push
sync_audit_status: out09_acceptance_closure_fast_forwarded_to_main
live_workspace_audit: accepted_exact_media_identity_and_manifest_hashes_match
current_title: OUT-09 accepted internal canonical closure
human_entrypoint: null
portable_entrypoint: null
review_open_command: null
review_server_restart_command: null
decision_required: none_out09_accepted_internal
review_status: accepted_internal
contract_repair_status: OUT09_REVIEW_ACCESS_STABILITY_AND_PLAYBACK_SAFETY_REPAIR_PASSED
user_feedback_overall: expected_internal_review_result_with_source_specific_blur_mosaic_observation
content_selection_status: accepted_internal
subtitle_presentation_timing_status: accepted_internal_exact_sha
endpoint_edit_status: accepted_internal_complete_boundary
remote_code_complete: true
local_artifact_available: true
local_artifact_role: accepted_same_machine_internal_review_evidence
portable_local_artifact_available: false
cross_machine_resume_class: tracked_builder_docs_portable_ignored_review_payload_same_machine_only
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: false
acceptance_granted: true
candidate_01_acceptance: accepted_internal
known_unrelated_test_failure: tests/test_vertical_short_candidate.py::test_out06_reviewed_japanese_break_hints_are_measured_and_semantic
known_unrelated_test_failure_2: tests/test_complete_narrative_short.py::test_out06_reviewed_wraps_are_repaired_in_package_readback
known_unrelated_test_failure_scope: same_two_failures_on_origin_main_29a1a519_and_out09_branch_17436ad_same_toolchain_not_branch_regression
source_specific_caption_suppression_observation: source_specific_caption_band_suppression_observed_acceptable_not_generalized
source_specific_caption_suppression_design_acceptance: false
out10_successor_candidate: OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION
out10_implementation_status: data_only_not_implemented
next_action: OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSIONをdata-only successorとして保持し、別sourceでの実装承認が得られるまで実装しない
active_artifact: clip-out09-second-source-short-repeatability-v0-001
canonical_main_head: branch_head_after_out09_acceptance_fast_forward
canonical_main_baseline: OUT-09 accepted internal exact SHA b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50
source_of_truth: false
owner_lane: output_video_cross_source_repeatability
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_09_SECOND_SOURCE_SHORT_REPEATABILITY.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
durable_context: docs/project-context.md, docs/idea-ledger.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-09は、exact MP4
`b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`について、
字幕と音声の一致、短い字幕の切替と可読性、初期状態での自動再生・突然の音がないこと、
foreground server方式でレビュー中のaccessが維持されること、発話途中ではない終端を
ユーザーが確認し、internal review用途としてacceptした。現在状態は
`OUT09_ACCEPTED_INTERNAL_CANONICAL_MAIN`で、同じartifact ID、source
`31.160–64.480s`、semantic `33.320s`、27 cue、MP4/ASS/SRT byteを維持する。

| 世代 | 画面上の字幕 | 背景canvas | exact MP4 | 判断状態 |
|---|---|---|---|---|
| initial | native caption + 長文burn-in | full-source blur | `300ee360...e0c9` | superseded、acceptanceなし |
| failed repair | 小さいnative captionのみ | full-source blurが字形を複製 | `3e7ef9d8...2916` | 人間が判読性・重複・霜ガラス感を指摘、acceptanceなし |
| current | JSON3由来の短い27 cueをcrisp burn-in | caption-free cropのみ | `b6b90a4b...73da50` | `accepted_internal`、canonical main |

人間観測は従前のAgent/machineによる「native captionは判読可能」という評価を上書きする。
readbackのrepair lineage index 2にはinitialとfailed repairの両SHA、失敗理由
`unreadable_native_caption_and_blurred_caption_duplication`を保持した。

access repair後は、人間が観測した「localhost serverが短時間で消える」「作業中に動画が
大きな音で自動再生された」という欠陥も解消した。worker processをserver寿命の根拠にせず、
未知のport ownerを終了したり別portへ逃げたりしない。ブラウザを閉じた際のRange切断も
正常なclient exitとして扱う。

上下のblur/mosaic状canvasは、source下部74pxのnative caption bandを構図から除外し、
`0,0,640,286`だけで9:16余白を補完したsource-specific caption suppressionとして観察された。
元の焼き込み字幕とshort cueの二重表示を防ぐ処理として今回だけacceptableであり、美観、
共通デザイン、caption bandのないsource、重要内容とcropが衝突するsource、production subtitle
designへ一般化しない。

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
| base-vs-branch | origin/main `29a1a519`とbranch `17436ad`で既知OUT-06 2件が同一失敗。default render command SHA `a863ee1a...7ebf`一致 |
| tests | review server / OUT-09 / current-state / shared consumerのdirect consumersは`81 passed, 2 deselected`。deselectした既知OUT-06 2件はbase/branchで別途比較 |

既知のOUT-06 reviewed-wrap 2件はorigin/mainとsource branchで同一に失敗したため、
pre-existing/environment-sensitive debtでありOUT-09 regressionではない。shared rendererの
default render commandはbyte-equivalentで、caption-free compositionは明示policyを渡した
OUT-09にだけ適用する。このdebtをOUT-10へ割り込ませない。

## 受入結果

- subtitle/audio一致: pass
- short cue切替と可読性: pass
- 初期自動再生・突然の音: なし
- foreground server access維持: pass
- endpoint: 発話途中ではなく区切りとして成立
- overall: `accepted_internal`

このtracked closureがacceptance authorityである。ignored packageのreadback/manifestは技術生成時の
`OUT09_STABLE_MANUAL_SAFE_REVIEW_READY`を保持していてよく、package欠落やserver停止は受入を
失効させない。initial `300ee360...e0c9`とfailed repair `3e7ef9d8...2916`へ受入を遡及しない。

## 閉じたgateと次の距離

- `episodes/`はignoredのままで、`git ls-files episodes`は0。packageは同一マシン証跡である。
- human transcript acceptance、production subtitle design/render、640x360 sourceのproduction
  画質、rights/material use、thumbnail、public/publishing/uploadは未承認。
- OUT-08以前の成果物は変更していない。OUT-09の技術修復からsuccessor acceptanceや
  3–5本portfolioの一般則を推論しない。
- OUT-09はaccepted internal canonical closureとして閉じた。次候補は
  `OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION`一件だけをdata-onlyで保持する。
- OUT-10は第三のdistinct sourceでcaption authority、crop strategy、cue density、source
  resolution、render時間、人間結果を共通schema比較する。明示承認まで実装しない。
