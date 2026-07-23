---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_EVIDENCE_BOUND_REVIEWABLE_ON_THANK_V1
progress_pct: 100
last_touched: 2026-07-24
current_slice: OUT-13
phase: human_editorial_review_pending
canonical_status: evidence_bound_editorial_candidate_reviewable_on_thank_v1
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
sync_baseline_head: da58a8212da88173d65c8b134368a57a278066e0
verified_implementation_head: this_commit_after_push
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 candidate 003 is evidence-bound and locally reviewable on Thank
human_entrypoint: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v003/review/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v003\review\open_preview.ps1
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v003\review\serve_preview.ps1
machine_readback: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v003/validation_readback.json
decision_required: human_editorial_accept_repair_or_reject_exact_candidate_003
review_status: machine_validated_worker_sample_observed_human_editorial_review_pending
remote_code_complete: true
local_artifact_available: true
local_artifact_role: ignored_same_machine_review_candidate
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_portable_exact_inputs_plan_and_output_require_private_transfer_or_new_identity_build
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
next_action: open_exact_candidate_003_and_record_human_editorial_accept_repair_or_reject_without_lifting_other_gates
active_artifact: clip-out13-editorial-video-candidate-v1-003
remote_handoff_tip: this_commit_after_push
source_of_truth: true
owner_lane: editorial_real_video_internal_review
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, artifacts/ARTIFACTS.md, docs/AUTOMATION_BOUNDARY.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-13 は、この Thank 端末に存在する入力を authority evidence まで再検証し、新しい不変 identity
`clip-out13-editorial-video-candidate-v1-003`として生成済みである。候補は 7 cut / 5 semantic
sections / 8 omitted ranges、128.795s の Timeline IR を持ち、生成 MP4 は 128.833333s、
82,594,810 bytes、SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`。
machine validation、authority binding、caption boundary、review package、fail-closed resume は通過した。

active branch は `codex/out-13-editorial-video-candidate-v1`。開始時に remote へ
`git pull --ff-only`を行い、HEAD / upstream は
`da58a8212da88173d65c8b134368a57a278066e0`で一致していた。main / origin/main は
`5d6f69a64d510508a1f78ab3111a7780913a019c`で一致し、OUT-13 は main 未統合である。
この文書を含む実装 commit が push 後の再開 tip になる。

## 候補 identity と履歴を分ける

| identity | 役割 | この端末の状態 | 次の扱い |
|---|---|---|---|
| `...-001` | 以前の source-host で成立した historical receipt | exact package はこの端末にない | source-host 履歴としてのみ参照 |
| `...-002` | この端末の初回 immutable rebuild | package は保持。caption authority 表示と plan SHA readback が訂正前 | 上書き・人間受理せず superseded evidence として保持 |
| `...-003` | 訂正済み active candidate | exact plan / MP4 / readback / review package が存在 | 人間が accept / repair / reject を判断 |

旧候補と現在候補は source identity 名が同じでも入力 SHA、plan、fingerprint、final SHA が異なる。
同じ artifact ID の復元や上書きとは扱わない。

## この端末へ結び付いた authority

| 面 | exact SHA / 読み戻し | 意味 |
|---|---|---|
| source MP4 | `6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a` | source receipt と material ledger の出力へ一致 |
| transcript | `4a7b4fd805bc607773f1f3e271d961415efddceae1f3e6a72f8e6c6220333495` | canonical transcript validation pass、source audio SHA も照合 |
| caption sidecar | `3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919` | `provider_json3_sidecar`。provider text/timing のみで、公式著者性は主張しない |
| rights snapshot | `4302c4a1ecc598d80c130050ae9f36ba6701c8f5a9ba46e5f01b519f4d417bb8` | parse / source identity / hash pass、status は `pending` |
| editorial plan input | `ca1aa5cd93687f3d656b18fe07d018def4ca42fd889ee900b96e49c09d423801` | review readback は入力ファイルの exact bytes を指す |
| resolved font | `Keifont` / `d5795bdff960c2b2ec5727ffeb79d836f8f11dac3015f6e16089a912e9cced6f` | fallback 不許可、実 font bytes を candidate へ固定 |

`authority_binding.json`は source receipt、material ledger、source audio、caption provenance、
rights snapshot、font bytes をまとめて `passed` と読み戻す。ただし speaker、歌詞、rights 適否、
production 品質は推定しない。

## 実artifactと検証

| 面 | 2026-07-24 live result |
|---|---|
| final media | H.264 High / AAC / yuv420p / 1920x1080、full decode / faststart pass |
| timeline | 7 cuts、5 sections、8 omitted ranges、source utilization 0.781671、mapping coverage 1.0 |
| caption | provider sidecar 102 cues、overlap / negative / orphan / split / duplicate / missing / unexpected 0 |
| audio/signal | -14.48 LUFS、-1.88 dBTP、最大隣接 cut 差 1.85 LU、black / silence event 0 |
| manifest | 24 payload rows、fingerprint `ba827411...2806`、self SHA `3d99372c...b1da1` |
| local package | 26 files / 87,113,363 bytes。`episodes/` ignored、tracked 0件 |
| resume | render 非実行、5 cache hits、final / manifest SHA 不変 |
| HTTP/browser | page 200、MP4 Range 206、desktop/mobile overflow なし、details は初期閉鎖 |
| media interaction | 初期 paused / muted / time 0、cut seek 40.856s、console / media warning・error 0 |
| visual sample | first/middle/last、全 cut 前後、短・通常・2行字幕 frame を Worker が実見。sampled frame に明白な二重 dialogue caption、safe-area 越境、破綻は見つからず |
| tracked regression | `uvx --from pytest --with Pillow pytest -q` → 616 passed / 332.09s |

package 自身の `visual_observation.status` は意図的に `unverified` のままであり、machine check を
人間観察へ昇格させていない。上記 visual sample は今回の Worker 観察で、人間の編集受理ではない。

## レビュー入口

候補の exact path が存在することを `Test-Path` で確認してから、次を foreground で開く。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v003\review\open_preview.ps1
```

review は candidate/source/plan/final hashes、authority、rights、cut 前後 seek、caption evidence、
machine validation を同じページで提示する。自動再生はなく、初期は paused / muted / time 0。
人間は exact candidate 003 に対して `accept` / `repair` / `reject` を記録する。repair の場合は
cut ID、caption ID、timestamp と観察事実を先に固定し、003 を上書きしない。

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

Git で portable なのは builder、tests、docs、contract まで。候補 003 と入力は ignored
same-machine evidence なので、別端末では承認済み private transfer で exact bytes を回収して全 SHA を
照合するか、別 identity で再生成する。`episodes/`を track しない。

## 次の判断

最短 critical path は `exact candidate 003 の人間編集レビュー -> 必要なら bounded successor repair ->
feature branch acceptance -> main integration 判断`。rights、production subtitle/design/render、
thumbnail、publishing、upload、public release は独立 gate であり、この technical green や
internal editorial acceptance から自動で開かない。
