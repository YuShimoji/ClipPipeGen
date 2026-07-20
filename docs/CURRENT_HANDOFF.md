---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT12_AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1
progress_pct: 100
last_touched: 2026-07-21
current_slice: OUT-12
phase: internal_automation_operational
canonical_status: automated_real_video_pipeline_operational_v1
active_branch: main
source_branch: codex/out-12-one-command-real-video-automation-v1
verified_implementation_head: a51a3fdb22ff44cb9e4528ed67c0c42d48d0d67a
remote_resume_contract: fetch_then_switch_main_then_read_this_file
current_title: OUT-12 one-command real long-form automation operational
human_entrypoint: http://127.0.0.1:8075/review/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\open_preview.ps1
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\serve_preview.ps1
machine_readback: episodes/out12_source05_one_command_real_video_20260721/review/out12_one_command_real_video_automation/validation_readback.json
decision_required: null
review_status: machine_validated_internal_review_available
remote_code_complete: true
local_artifact_available: true
local_artifact_role: ignored_same_machine_real_long_form_operational_proof
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_only_real_source_and_output_media_same_machine
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: false
automation_acceptance_granted: true
next_action: optional_content_inspection_or_next_explicitly_approved_gate_only
active_artifact: clip-out12-one-command-real-video-automation-v1-001
canonical_main_head: 9879d194494cc7f462f373612d30ecfbd0c70471
canonical_main_head_role: out12_integrated_code_docs_baseline_before_post_sync_receipt
source_of_truth: true
owner_lane: real_video_internal_automation
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json
upstream_parity: 0 0
handoff_base_head: 9879d194494cc7f462f373612d30ecfbd0c70471
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-11でShort候補のexact human acceptanceを閉じた後、OUT-12として実sourceから実動画を
一コマンド生成するvertical sliceを完成させた。`build-real-video`は取得済みsourceまたは
episode material identityを受け、provenance、content fingerprint、scene/black/silence解析、
chronological Timeline IR、caption timing remap、H.264/AAC render、full validation、manifest、
localhost reviewをatomic packageにする。

実runは`youtube:gUwJBRUIWow`全長を11 cutに分割し、260.693767s / 1920x1080 / H.264/AAC、
142,789,781 bytes、SHA
`5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584`を生成した。全13 validation
checks、contact sheets/waveform目視、HTTP 200 / Range 206、desktop/mobile、safe media state、cut
seek、console/media error 0をpass。`--resume`は2.095秒、render非実行、同一SHAで閉じた。

## 別端末での再開

```powershell
git fetch --prune origin
git switch main
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

tracked code/docs/testsはportableだが、実source、最終MP4、evidence、localhost packageは
`episodes/`配下のsame-machine ignored artifactで、Gitには入らない。別hostでは同じsource bytesを
用意するか、そこで新しいlocal artifactを生成する。

## 実行入口

```powershell
uvx python -m src.cli.main build-real-video `
  --source episodes\out11_source05_dramatic_xviltration_20260720\materials\src_video_out11_source05\source_video.mp4 `
  --authority-readback episodes\out11_source05_dramatic_xviltration_20260720\review\out11_source05_candidate\candidate_readback.json `
  --output-dir episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation `
  --profile long-form --target-duration 300 --resume --review-port 8075 --format json
```

`--resume`はfingerprintとmanifest payloadが一致する成功済みpackageにだけ使う。入力やartifactが
変わった場合はfail closedする。新規生成は意図を確認して`--force`へ切り替える。

## Artifactと検証証跡

| 面 | 確定値 | 再開上の意味 |
|---|---|---|
| source | `youtube:gUwJBRUIWow`; SHA `8decc04d...d0037cf`; 260.643991s | 3分以上を満たした唯一のpreflight候補 |
| timeline | full-source scene partition、11 cut、3 sections、coverage 1.0 | chronologyとsource mappingを機械追跡可能 |
| final | SHA `5d391ffd...a584`; 260.693767s; H.264/AAC 1920x1080 | human reviewを含まないautomation acceptance identity |
| signal | -14.15 LUFS / -1.44 dBTP、最大cut差1.27 LU、max black 0.7007s、silence 0 | 初回のAV/peak失敗をcorrective passで修復済み |
| captions | timing cue 468、overlap/negative/orphan 0、native baked text保持 | 歌唱・歌詞・speaker・意味は未確認のまま |
| resume | analysis/caption/render/validation cache hit、render false、同一SHA | 高コスト処理を安全に再利用できる |
| review | `review/index.html`、3 evidence images、11 seek controls | foreground localhostで任意内容確認可能 |

## 境界

OUT-12で受理したのはinternal real-video automation routeであり、作品内容、rights、production
subtitle design、production render/public use、thumbnail、winner、publishing/uploadの承認ではない。
次へ進む場合は、これらを一括で開けず、目的が明示されたgateを一つだけ別sliceで扱う。
