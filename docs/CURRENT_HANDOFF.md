---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1
progress_pct: 100
last_touched: 2026-07-22
current_slice: OUT-13
phase: internal_editorial_review_ready
canonical_status: editorial_representative_video_reviewable_v1
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
verified_implementation_head: this_commit_after_push
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 caption-evidence editorial representative video review ready
human_entrypoint: http://127.0.0.1:8076/review/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\open_preview.ps1
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\serve_preview.ps1
machine_readback: episodes/out13_editorial_video_candidate_20260722/review/out13_editorial_video_candidate/validation_readback.json
decision_required: internal_editorial_composition_subtitle_picture_audio_review
review_status: machine_validated_human_editorial_review_available
remote_code_complete: true
local_artifact_available: true
local_artifact_role: ignored_same_machine_caption_evidence_editorial_video
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_only_source_and_output_media_same_machine
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: true
automation_acceptance_granted: true
editorial_acceptance_granted: false
next_action: human_reviews_one_out13_mp4_for_editorial_structure_subtitle_presentation_picture_audio_then_choose_one_explicit_gate
active_artifact: clip-out13-editorial-video-candidate-v1-001
remote_handoff_tip: this_commit_after_push
source_of_truth: true
owner_lane: editorial_real_video_internal_review
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, artifacts/ARTIFACTS.md, docs/AUTOMATION_BOUNDARY.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-12の一コマンド実動画automationを基礎に、OUT-13として明示的なeditorial planを受ける
`build-editorial-video-candidate`を追加した。planはsource identity / SHA、source in/out、output order、
section、editorial role、選択理由、continuity/context evidence、transcript segment IDs、transition、
omitted rangesを保持し、caption/transcript evidenceから6つの非連続範囲を時系列どおりに接続する。
これにより、scene partitionやuniform samplingではなく、何を残し何を短縮したかを人間と機械の双方が
同じMP4上で監査できる。

実runは既存official hololive source `youtube:7J5aS_pcBj4`（164.768798s、1920x1080、source SHA
`e2206cef93855e6005e4cc099bedc29d291eda6f2e1c66039c961e93621f1889`）を使用した。電話での挑戦、
二人の対戦、三人との最終戦、召喚された門番長との終結を4 section / 6 cutへ保持し、待機、移動、
反復battle、反復叫声、credits等6範囲を除外した。finalは122.866016s、source利用率74.542%、
H.264 High/AAC 1920x1080、73,776,611 bytes、SHA
`84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2`。

公式JA JSON3 77 cueをKeifont 100px、line height 115px、white body、black 8px outline / 2px
shadow、最大2行でburn-inした。speaker identityはcaption textから推定せずbadgeを描画していない。
selected source framesに対話captionがないこととfinal evidenceを対比し、二重表示、safe-area overflow、
overlap、negative duration、orphan cueはいずれも0。通常発話、長文2行、0.534s短時間cueのfinal frame
evidenceもpackage内にある。

## artifactと検証の読み方

| 面 | 確定値 | 監修時の意味 |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-001`; `EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1` | OUT-12 operationalからhuman editorial review可能な状態へ進んだ |
| source authority | official JSON3 SHA `3c15535f...d169919`; transcript SHA `ef928d4e...b42d6`; rights snapshot SHA `e6ea9471...64c12` | 文言/timing/cut根拠は追えるがspeaker・lyrics・rights判断は含まない |
| timeline | 6 cuts、4 sections、6 omissions、mapping 1.0、uniform/arbitrary-thirds false | 各cutのreason/context/segment IDsをreview表から追跡できる |
| media | 122.866016s、SHA `84ed7aa6...791d7e2`、-14.61 LUFS、-1.58 dBTP、最大cut差0.94 LU | 全体のテンポ、画面、字幕、音声を一本で判断できる |
| validation | review-visible 19 checks pass、full decode/faststart/timestamps/A/V/black/silence/caption/mapping pass | 技術欠陥を人間の編集判断へ混ぜずに済む |
| review | desktop/mobile overflow false、initial paused/muted/time0、seek 14.714s一致、page 200、Range 206、console/media error 0 | 単一入口を開けば探索なしでvideo→cut/omission→evidence→checksの順に確認できる |
| resume | input fingerprint `051832b9...e3d8`; 0.328s、renderなし、同一video/manifest SHA | 別inputの古いcacheを誤利用せず同じartifactを再開できる |
| manifest | 23 payloads、self-integrity SHA `8f0be672d847ea7b066a6ec932790f91601fd499956987813ec7edc42b0c02e8` | package identityと各evidenceのhashを一括監査できる |

## 同一マシンでレビューを開く

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\open_preview.ps1
```

clean URLは`http://127.0.0.1:8076/review/index.html`。launcherはforeground serverを起動する。
review終了時はそのPowerShellで`Ctrl+C`を使う。review pageは動画を先頭に置き、その下にselected timeline、
omitted ranges、source/final evidence、waveform、machine validationを一列で提示する。cutごとの`seek`で
該当output位置へ移動できる。

同一inputのmanifest/fingerprintだけを高速確認する場合は次を実行する。

```powershell
uvx --with Pillow python -m src.cli.main build-editorial-video-candidate `
  --source episodes\jp_pilot01_hololive_bancho_20260525\materials\src_video_jp_pilot01\source_video.mp4 `
  --source-identity youtube:7J5aS_pcBj4 `
  --editorial-plan episodes\out13_editorial_video_candidate_20260722\editorial_plan_input.json `
  --transcript episodes\jp_pilot01_hololive_bancho_20260525\transcript.json `
  --caption-track episodes\jp_pilot01_hololive_bancho_20260525\source_subs\7J5aS_pcBj4.ja.json3 `
  --rights-manifest episodes\jp_pilot01_hololive_bancho_20260525\rights_manifest.json `
  --output-dir episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate `
  --resume --review-port 8076 --format json
```

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

tracked code/docs/testsはportableだが、source、editorial plan input、final MP4、evidence、localhost packageは
ignored `episodes/`配下にあり、別cloneには届かない。別hostでは同一source/caption/transcript/rights/plan
bytesを用意して実行し直す。`episodes/`をGitへ追加してportable化しない。

## 次の判断

最も直接的な次の動きは、一本のOUT-13 MP4について編集構成、字幕presentation、画面・音声品質を
internal human reviewすること。受理する場合もexact video SHAへbindし、rightsやproduction利用へ
自動昇格させない。次の実装を先に進めるなら、human reviewで見つかったsource-specificな修正、rights
判断、production subtitle/render gateのいずれか一つだけを明示的に開く。thumbnail、publishing、uploadは
本artifactのconsumerではなく、引き続き別gateである。
