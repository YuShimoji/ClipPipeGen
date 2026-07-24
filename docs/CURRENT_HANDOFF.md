---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_CANDIDATE_005_IMMUTABLE_TRANSITIVELY_LINEAGE_BOUND_REVIEWABLE_V1
progress_pct: 100
last_touched: 2026-07-24
current_slice: OUT-13
phase: human_editorial_review_pending
canonical_status: immutable_transitively_lineage_bound_reviewable_v1
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
sync_baseline_head: 3fdad157c09cc925a50750135e14fff5faa832f2
verified_implementation_head: this_commit_after_push
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 candidate 005 is strongly immutable, content-lineage-bound, and locally reviewable on Thank
human_entrypoint: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v005/review/index.html
portable_entrypoint: null
review_open_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
review_server_restart_command: powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\serve_preview.ps1
machine_readback: episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v005/validation_readback.json
decision_required: human_editorial_accept_repair_or_reject_exact_candidate_005_with_candidate_004_retained_as_parallel_review_target
review_status: machine_validated_browser_verified_human_editorial_review_pending
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
automation_acceptance_scope: evidence_bound_explicit_plan_rendering_only_semantic_selection_unverified
editorial_acceptance_granted: false
next_action: open_exact_candidate_005_and_record_human_editorial_accept_repair_or_reject_without_lifting_other_gates
active_artifact: clip-out13-editorial-video-candidate-v1-005
remote_handoff_tip: this_commit_after_push
source_of_truth: true
owner_lane: editorial_real_video_internal_review
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, artifacts/ARTIFACTS.md, docs/AUTOMATION_BOUNDARY.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-13 は、この Thank 端末に存在する入力を content-sensitive authority evidence まで再検証し、
成功 package を schema / state / identity に依存せず不変にする successor identity
`clip-out13-editorial-video-candidate-v1-005`として生成済みである。
候補は 7 cut / 5 semantic
sections / 8 omitted ranges、128.795s の Timeline IR を持ち、生成 MP4 は 128.833333s、
82,594,810 bytes、SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`。
machine validation、signed PCM audio / anonymous provider-caption lineage、symlink-free closed
manifest、caption boundary、review package、package 非変更の fail-closed resume は通過した。

active branch は `codex/out-13-editorial-video-candidate-v1`。開始時に remote へ
`git pull --ff-only`を行い、HEAD / upstream は
`3fdad157c09cc925a50750135e14fff5faa832f2`で一致していた。main / origin/main は
`5d6f69a64d510508a1f78ab3111a7780913a019c`で一致し、OUT-13 は main 未統合である。
この文書を含む実装 commit が push 後の再開 tip になる。

## 候補 identity と履歴を分ける

| identity | 役割 | この端末の状態 | 次の扱い |
|---|---|---|---|
| `...-001` | 以前の source-host で成立した historical receipt | exact package はこの端末にない | source-host 履歴としてのみ参照 |
| `...-002` | この端末の初回 immutable rebuild | package は保持。caption authority 表示と plan SHA readback が訂正前 | 上書き・人間受理せず superseded evidence として保持 |
| `...-003` | media-reviewable technical predecessor | 26 files / 87,113,363 bytes を開始時 inventory のまま保持 | accepted / rejected とせず preserved evidence としてのみ参照 |
| `...-004` | v3 closed-package / energy-lineage predecessor | exact plan / MP4 / readback / review package を開始時 digest のまま保持 | verdict を推定せず、005 と並行する人間レビュー対象として保持 |
| `...-005` | strong immutability / content-lineage successor | exact plan / MP4 / readback / review package が存在 | 人間が accept / repair / reject を判断 |

旧候補と現在候補は source identity 名が同じでも入力 SHA、plan、fingerprint、final SHA が異なる。
同じ artifact ID の復元や上書きとは扱わない。

## この端末へ結び付いた authority

| 面 | exact SHA / 読み戻し | 意味 |
|---|---|---|
| source MP4 | `6f78657ea251f623eee75b3b4be64af3b1bad1f6bc028eb00e38baebd076103a` | source receipt と material ledger の出力へ一致 |
| transcript | `4a7b4fd805bc607773f1f3e271d961415efddceae1f3e6a72f8e6c6220333495` | canonical transcript validation pass、source audio SHA も照合 |
| caption sidecar | `3c15535f9c84ddd377ce23685ea961716b57621e9c8b5e61d3412c4b3d169919` | `provider_json3_sidecar`。provider text/timing のみで、公式著者性は主張しない |
| rights snapshot | `4302c4a1ecc598d80c130050ae9f36ba6701c8f5a9ba46e5f01b519f4d417bb8` | parse / source identity / hash pass、status は `pending` |
| editorial plan input | `27ef1aa9d7aa29267e43d4b9b33dc17051acbf8f5b38dc4a3b50649e1ca6dac2` | 004 の cut / section / caption / typography / render contract を保ち、v4 identity / evidence だけを successor 化 |
| source audio lineage | video PCM `48f9d946...44b8` / audio PCM `f608fd1a...fcfcd`、coverage `0.999647612317`、signed similarity `0.947803984`、gain `0.943714876`、NRMSE `0.318853585`、lag `0.036312s` | energy envelope は coarse lag 専用。符号付き波形・正 gain・全域残差で exact video から transcript audio への content lineage を検証 |
| caption provider identity | `youtube:7J5aS_pcBj4`、anonymous acquisition receipt SHA `aeff5613...90e4`、caption provenance `e4680280...65e` | credential / cookie / OAuth / MFA なしの再取得結果を provider ID と exact JSON3 SHA へ結合 |
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
| manifest | closed set 24 payload rows + excluded `run_manifest.json`、payload digest `8257a15c...c054`、fingerprint `bbeb2514...a6a0b`、self SHA `5d7550a7...d32b`。symlink / junction / external target は拒否 |
| local package | 25 files / 87,123,995 bytes。package-tree digest `ed45fd4c...040`。`episodes/` ignored、tracked 0件 |
| resume / rejection | render 非実行、5 cache hits、package-tree digest 前後一致。failure / resume は sibling `.run_journal` のみを更新 |
| HTTP/browser | page 200、MP4 Range 206、横 overflow なし、4 evidence images loaded、7 cut / 8 omission / 14 seek controls |
| media interaction | 初期 paused / muted / time 0、readyState 4、1920x1080、128.833333s、console / media warning・error 0 |
| visual boundary | package evidence と browser surface を確認。package `visual_observation` は `unverified`、人間の全編視聴・受理は未実施 |
| tracked regression | final full-suite result is recorded in this mission commit validation; targeted OUT-13 module is 58 passed |

package 自身の `visual_observation.status` は意図的に `unverified` のままであり、machine check や
browser smoke を人間観察へ昇格させていない。人間の全編視聴・編集受理は未実施である。

## レビュー入口

候補の exact path が存在することを `Test-Path` で確認してから、次を foreground で開く。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
```

review は candidate/source/plan/final hashes、authority、rights、cut 前後 seek、caption evidence、
machine validation を同じページで提示する。自動再生はなく、初期は paused / muted / time 0。
人間は exact candidate 005 に対して `accept` / `repair` / `reject` を記録する。candidate 004 は
同じ MP4 bytes を持つ parallel review target として verdict 未記録のまま保持する。repair の場合は
cut ID、caption ID、timestamp と観察事実を先に固定し、004 / 005 を上書きせず 006 以降を割り当てる。

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

Git で portable なのは builder、tests、docs、contract まで。候補 004 / 005 と入力は ignored
same-machine evidence なので、別端末では承認済み private transfer で exact bytes を回収して全 SHA を
照合するか、別 identity で再生成する。`episodes/`を track しない。

## 次の判断

最短 critical path は `exact candidate 005 の人間編集レビュー -> 必要なら bounded successor repair ->
feature branch acceptance -> main integration 判断`。rights、production subtitle/design/render、
thumbnail、publishing、upload、public release は独立 gate であり、この technical green や
internal editorial acceptance から自動で開かない。
