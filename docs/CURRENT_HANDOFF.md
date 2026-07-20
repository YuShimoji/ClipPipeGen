---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT11_HUMAN_REVIEW_REPAIRS_COMBINED_REVIEW_READY
progress_pct: 95
last_touched: 2026-07-21
current_slice: OUT-11
phase: human_review_ready
canonical_status: repaired_two_candidate_combined_review_ready
active_branch: codex/out-11-five-source-short-portfolio-wave-v0
verified_implementation_head: branch_head_after_push
source_branch_tip: branch_head_after_push
closure_branch: null
remote_resume_contract: fetch_then_switch_codex_out11_branch_then_read_this_file
current_title: OUT-11 repaired OUT-10 and SOURCE-05 combined review ready
human_entrypoint: http://127.0.0.1:8074/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\open_preview.ps1 -Serve
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\serve_preview.ps1
decision_required: review_exact_repaired_out10_and_source05_once
review_status: pending_human_review_for_two_repairs
remote_code_complete: true
local_artifact_available: true
local_artifact_role: ignored_same_machine_two_video_review_one_accepted_receipt_and_five_source_scorecard
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_only_media_packages_same_machine
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: true
acceptance_granted: false
winner_selected: false
portfolio_subtitle_differentiation_debt: open_for_later_system_review_not_decided_here
next_action: 修復後OUT-10とSOURCE-05を同じページで一度だけ確認し、候補別の自由記述を新exact SHAへ結ぶ
active_artifact: clip-out11-five-source-short-portfolio-wave-v0-002
canonical_main_head: 663c6e6f19d1f176b96bc04c90993b00925b039c
source_of_truth: true
owner_lane: output_video_cross_source_portfolio
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_10_THIRD_SOURCE_PORTFOLIO_EXPANSION.md, docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

2026-07-21の人間レビューを旧exact SHAへ記録し、SOURCE-04は問題なしとしてexact bytesを
accepted receiptへ移した。OUT-10は診察場面を閉じる34.785sまで終端だけを延長し、SOURCE-05は
同一recording内の202.586sからsource EOF 260.643sまでを選び直した。旧SOURCE-05に付いていた
native lyric、歌唱、歌詞、音楽句という未確認の説明はcurrent authorityから除去した。

現在の唯一の判断面は、修復後OUT-10と修復後SOURCE-05を順に並べたlocalhostレビューである。
SOURCE-04は合格済み受領証だけを表示し、動画は統合packageへ複製せず、再視聴を求めない。

## Exact review package

| 項目 | 現在値 | 意味 |
|---|---|---|
| artifact | `clip-out11-five-source-short-portfolio-wave-v0-002` | 修復二本の最終判断面 |
| state | `OUT11_HUMAN_REVIEW_REPAIRS_COMBINED_REVIEW_READY` | 機械検証完了・人間判断待ち |
| package | `episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/` | ignored same-machine artifact |
| readback | SHA `4e6160915d80bdcef58cfa407e6be3e74daf4be002dc14d2a9b02f6fda54b406` | 2 review candidates、1 receipt、境界の読み戻し |
| manifest | file SHA `e72de3fe092aafb72aa7dd59208c2c07e715c307ce9aac92ada61ae8e632a390`; self SHA `58276967cb2328f3a8b9ea8813bb85a4847f84e26e8bd465206c56d3e87da7bd` | 13 payloadとsource packageをhash bind |
| scorecard | SHA `4b388531fb3093fd10449d7722656d2ea8dcae8bf9e4d0783d0b63f61ed0d2c9` | 5 source / active media 2 / receipt 1 / winnerなし |
| access | `http://127.0.0.1:8074/index.html` | server起動中だけ有効 |

## 候補別の判断と現在値

| slot | 旧判断対象 | 現在のexact bytes | 現在状態と次の確認 |
|---|---|---|---|
| OUT-10 | `a53d0416...134f2`, `0.000–30.014s`: 導入は成立したが意識確認場面が閉じない | `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd` / 19,319,488 bytes / `0.000–34.785s` | 意識確認、患者反応、最終台詞が自然に閉じ、34.800sの別紹介を含めないか確認 |
| SOURCE-04 | `465d732c...16524`: 一本として自然、追加違和感なし | 同じSHA `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524` / 同じ8,523,260 bytes | `accepted_internal` receipt。再render・再視聴なし |
| SOURCE-05 | `370850c5...b578`, `202.586–217.650s`: 新画面直後に停止。歌唱・歌詞説明も未確認 | `b4a01413202e3e177a11dc42754d38f5a4b7b10cd7c7bec0aa43536d440a4969` / 20,469,323 bytes / `202.586–260.643s` | カード列からtitle/credit holdとsource EOFまでがaudio-visual unitとして成立するか確認 |

SOURCE-05のsource-native textは保持しているが、official JSON3はtiming landmarkに限定する。
speaker、歌唱、歌詞、意味内容は未確認で、reviewerにもその確認を要求しない。

## 検証済み

- OUT-10とSOURCE-05はsource/contact sheet/waveform/caption/shot transitionの事前観測後、各1回の
  repair renderで到達。corrective render 0。
- 両方H.264/AAC、1080x1920、30fps、yuv420p、full decode、faststart pass。
- OUT-10は50 cue containment、`-13.79 LUFS/-1.45 dBTP`、black/silence 0。
- SOURCE-05は`-14.02 LUFS/-1.49 dBTP`、silence 0、black 0.766667sで1.5s threshold内。
- 最終6秒contact sheetとwaveformを目視し、OUT-10の連続反応・最終字幕、SOURCE-05の
  title/credit hold・自然な音声減衰を確認。
- SOURCE-04は作業後もSHA `465d732c...16524` / 8,523,260 bytesで完全一致。combined packageに
  SOURCE-04 MP4なし、receipt evidenceだけ。
- localhost page 200、OUT-10/SOURCE-05ともRange 206 `bytes 0-1023/<exact-size>`。
- desktop 1280とmobile 390でoverflowなし、media errorなし、readyState 4。
- clean URLは両方paused/muted/currentTime 0。`?qa-playback=1`だけ先頭をmuted再生し、SOURCE-05を
  再生するとOUT-10がpauseする。console warning/error 0。
- 検証後にbrowser tabとport 8074 serverを停止し、listener 0を確認。
- `uvx --with Pillow pytest -q`は580 passed。changed-scope Ruff、JSON parse、`git diff --check`もpass。

## 今回の一回の人間確認

起動:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\open_preview.ps1 -Serve
```

URL: `http://127.0.0.1:8074/index.html`

1. SOURCE-04の合格受領証を確認する。再生対象ではない。
2. OUT-10「診察場面の終端修復」を見る。source `0.000–34.785s`。
3. SOURCE-05「Dramatic XViltration」を見る。source `202.586–260.643s`。
4. 返却してほしい自由記述:
   「修復後OUT-10は新しい診察場面の反応と台詞まで自然に閉じたか。修復後SOURCE-05はカード列から
   最終タイトルまでの音声・映像・終端が一つの単位として成立したか。二本それぞれに明確な
   違和感があれば自由に教えてください。」

clean URLの期待状態は両方停止・mute・時刻0・音量上限25%、同時再生なし。review終了時はserverを
起動したforeground PowerShellで`Ctrl+C`を押す。

## 維持する境界と次の先端

- `episodes/`はignoredでGitへ追加しない。remote cloneにmediaはない。
- OUT-08/09とSOURCE-04のaccepted_internal判断を再開・変更しない。
- caption、neutral matte、speaker colorを5 source共通production標準へ一般化しない。
- rights、production render/subtitle/image quality、thumbnail、winner、public/publishing、
  upload/OAuth/visibility/made-for-kidsは未承認。
- 二本が受理された場合だけ、OUT-10 closureを先、OUT-11 closureを後に扱う統合計画へ進める。
- SOURCE-05だけに違和感が残る場合は同じrecordingのbounded repairまたはpark/rejectを選び、
  OUT-10とSOURCE-04の判断を再開しない。
