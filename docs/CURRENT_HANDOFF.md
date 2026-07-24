---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: EDIT_READY_SOURCE_PACKET_OPERATIONAL_V1
progress_pct: 100
last_touched: 2026-07-24
current_slice: SH-10
phase: edit_ready_input_operational
canonical_status: edit_ready_source_packet_operational_v1
active_branch: codex/edit-ready-source-packet-v1
source_branch: main
verified_implementation_head: ff3ad3ce79c8ac72b0c73be8eecae6c1044694db
remote_resume_contract: fetch_then_switch_codex_edit_ready_source_packet_v1_then_read_this_file
current_title: provenance-bound edit-ready Source Packet operational
human_entrypoint: episodes/edit_ready_source_packet_20260724/source_packet/clip-edit-ready-source-packet-v1-001/source_packet_report.html
portable_entrypoint: null
review_open_command: Invoke-Item episodes\edit_ready_source_packet_20260724\source_packet\clip-edit-ready-source-packet-v1-001\source_packet_report.html
review_server_restart_command: null
machine_readback: episodes/edit_ready_source_packet_20260724/source_packet/clip-edit-ready-source-packet-v1-001/source_packet.json
decision_required: null
review_status: machine_validated_edit_ready_input_available
remote_code_complete: true
local_artifact_available: true
local_artifact_role: ignored_same_machine_source_packet_operational_proof
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_only_source_media_caption_and_packet_same_machine
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
production_image_quality_acceptance: false
thumbnail_acceptance: false
winner_selected: false
public_or_publishing_acceptance: false
human_review_pending: false
automation_acceptance_granted: true
next_action: consume_the_packet_in_minimal_editorial_planning_and_timeline_ir_without_reacquisition
active_artifact: clip-edit-ready-source-packet-v1-001
canonical_main_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
canonical_main_head_role: branch_base_current_origin_main_at_mission_start
remote_handoff_tip: this_commit_after_push
handoff_sync_status: final_handoff_commit_pushed_and_parity_verified
source_of_truth: true
owner_lane: shared_edit_ready_input
related: docs/RUNTIME_STATE.md, docs/SCHEMAS/v1/edit_ready_source_packet.md, docs/AUTOMATION_BOUNDARY.md, artifacts/ARTIFACTS.md, docs/SUPERVISOR_STATUS_REPORT.md
upstream_parity: 0 0
handoff_base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
---

# Current Handoff - ClipPipeGen

## 2026-07-24 Edit-Ready Source Packet

`build-edit-ready-source-packet` により、URL/local sourceから video/audio acquisition、
rights snapshot、material ledger、caption/real transcript authority、normalized segments、
consumer readiness、input fingerprint、artifact/packet integrityまでを一コマンドで結ぶ
SH-10がoperationalになった。実証artifactは
`episodes/edit_ready_source_packet_20260724/source_packet/clip-edit-ready-source-packet-v1-001/`
にあり、packet JSONとpassive HTML readbackを持つ。`episodes/`はignoredでportableではない。

| 確認面 | 実測値 | 次工程への意味 |
|---|---|---|
| source | `youtube:7J5aS_pcBj4`; SHA `e2206cef...f1889`; 164.768798s; 1920x1080 | consumerは取得元とexact bytesをpacket identityから追跡できる |
| authority | `official_provider_caption`; JA 105 segment; 122.99s; coverage `0.746439869` | fixtureを探索せず、元event mappingを保った編集入力を読める |
| binding | fingerprint `fcd7c30b...da87`; integrity `4398a858...0fe9` | input差・packet改変・artifact破損をfail closedにできる |
| resume | 同一入力は`acquisition_executed=false`、異なるidentityはfingerprint mismatch | 高コスト取得を反復せず、古いcacheの誤利用を拒否する |
| negative | 実fixture transcriptはacquisition前に`fixture_transcript_authority_forbidden` | fake evidenceを成功扱いしない |

再開コマンド:

```powershell
python -m src.cli.main build-edit-ready-source-packet `
  --packet-id clip-edit-ready-source-packet-v1-001 `
  --episode-id edit_ready_source_packet_20260724 `
  --source-locator episodes/jp_pilot01_hololive_bancho_20260525/materials/src_video_jp_pilot01/source_video.mp4 `
  --source-identity youtube:7J5aS_pcBj4 `
  --language ja `
  --rights-manifest episodes/jp_pilot01_hololive_bancho_20260525/rights_manifest.json `
  --caption-track episodes/jp_pilot01_hololive_bancho_20260525/source_subs/7J5aS_pcBj4.ja.json3 `
  --caption-authority provider_official `
  --caption-provider-locator youtube-caption:7J5aS_pcBj4:ja `
  --root episodes --resume --format json
```

次の実装境界は、この packet を直接読む最小 editorial planning / Timeline IR consumer。
source acquisitionやauthority選択をconsumer側へ複製せず、packetのready stateとintegrityを
入口 gate にする。rightsはpending、editorial/production/public/uploadはfalse。保護対象
OUT-13 (`codex/out-13-editorial-video-candidate-v1`,
`clip-out13-editorial-video-candidate-v1-001`, video SHA `84ed7aa6...791d7e2`)は不変で、
human editorial reviewもpendingのまま。

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

判断経緯と再開順序は`docs/project-context.md`、`docs/decision-log.md`、`docs/idea-ledger.md`にも
同期済み。handoff直前の検証済みmainは`f9cfc1194368087c49ffd98b69f880d6109cabfb`で、最終remote
handoff tipは本commitになる。別端末では取得した`main`のHEADを正とし、古い履歴capsuleからbranchや
next actionを復元しない。

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

次の安全な入口は、異なる3分以上の実source一本でrepeatabilityを検証するか、rights、production
subtitle design/render、thumbnail、private transportのいずれか一つを明示承認して開くこと。OUT-12の
任意内容確認は可能だが、すでに閉じたautomation acceptanceを再び判断待ちへ戻さない。
