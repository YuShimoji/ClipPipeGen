---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: review_ready
health: OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY
progress_pct: 100
last_touched: 2026-07-14
current_slice: OUT-08
phase: human_review
canonical_status: internal_review_ready_human_decision_pending
active_branch: codex/out-08-real-unused-range-short-minibatch-v0
current_title: OUT-08 real unused-range vertical Shorts mini-batch review
human_entrypoint: http://127.0.0.1:8071/index.html
portable_entrypoint: null
review_open_command: powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out08_real_unused_range_short_minibatch\open_preview.ps1 -Port 8071
review_server_restart_command: powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out08_real_unused_range_short_minibatch\serve_preview.ps1 -Port 8071
machine_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/batch_readback.json
operator_readback: episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/index.html
decision_required: out08_whole_candidate_human_review
review_status: OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY
remote_code_complete: true
local_artifact_available: true
local_artifact_role: active_same_machine_internal_review_evidence
portable_local_artifact_available: false
cross_machine_resume_class: same_machine_ignored_package
active_rebuild_contract: null
parked_predecessor_rebuild_contract: artifacts/ACTIVE_REBUILD.json
evidence_revision: thank-6f78657e-out08-real-unused-range-minibatch-v1
last_verified_host: DESKTOP-H53P1T4
last_verified_host_label: Thank
last_verified_host_local_artifact_available: true
last_verified_host_entrypoint: http://127.0.0.1:8071/index.html
local_artifact_evidence_receipt: episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/batch_manifest.json
review_server_status: running_pid_39652_exact_serve_review_command_verified
rights_approval: pending
production_acceptance: false
production_subtitle_design_acceptance: false
public_or_publishing_acceptance: false
human_review_pending: true
acceptance_granted: false
target_candidate_count: 2
minimum_candidate_count: 1
actual_candidate_count: 2
next_action: 追加Shorts候補ごとに、一本の編集単位として成立するか、テンポ・境界・字幕・音声に違和感があれば自由記述してください。
active_artifact: clip-out08-real-unused-range-short-minibatch-v0-001
canonical_main_head: 4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9
canonical_main_baseline: OUT-07 PARK_PROVISIONAL_USABLE parked predecessor
source_of_truth: false
owner_lane: shared_infra
related: docs/RUNTIME_STATE.md, docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md, artifacts/ARTIFACTS.md, docs/dashboard/project-status.json, artifacts/ACTIVE_REBUILD.json
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-07 は `PARK_PROVISIONAL_USABLE` として main commit
`4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9` に着地済みである。選定、
canonical 化、default template 化は行っておらず、追加 OUT-07 thumbnail
iteration も禁止した。その parked predecessor から OUT-08 branch を切り、
既存 Shorts が使っていない実素材範囲から target 2 / minimum 1 に対して
二本の vertical Shorts 候補を一つの review page にまとめた。

現在の human entrypoint は `http://127.0.0.1:8071/index.html`。同端末では
PID `39652` が exact `src.cli.serve_review` command で配信している。package は
次の ignored path にあり、Git へは追加しない。

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/
```

## 判断できる二本

| 候補 | 使った authority | semantic / media | 字幕 | SHA-256 | 確認する編集効果 |
|---|---|---:|---:|---|---|
| `candidate_01` | `cut_004` `50.868–60.277` + `cut_005` `60.277–79.163` | `28.295s` / `28.266667s` | 17 | `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` | 勝負の提示から認識違い、勝利扱いと困惑した別れまでが短い一場面として成立するか。 |
| `candidate_02` | `cut_006` tail `81.298–98.315` + `cut_007` `98.315–116.467` + `cut_008` `116.934–135.219` + dependent payoff `137.054–138.055` | `54.455s` / `54.5s` | 55 | `c6d3ff01624c359c1ca0030bb360eb3906e6b35a62ec439c0efb14378e9c8320` | 遭遇から対立の進展、短い勝敗 payoff までが一本の流れとして持続するか。 |

`cut_009` は final cut decision `reject` のまま変更していない。candidate 02
が含むのは `sub_102` に対応する 1.001 秒の dependent payoff だけで、
cut promotion ではない。二枚の navigation image は候補間の移動補助であり、
decorated thumbnail、thumbnail candidate、thumbnail acceptance ではない。

## 機械確認と人間判断の境界

両動画は H.264/AAC、1080x1920、30fps、yuv420p、faststart。full decode は
通過し、0.5 秒以上の black interval と -50dB で 1.5 秒以上の silence
interval は検出されていない。subtitle repair 前の browser check では二本とも
`readyState=4`、media error `null`、desktop/mobile overflow なし、console
clean。最終 repair package は HTTP 200、Range 206、ffprobe、full decode を
再確認した。automation browser で native control の direct seek は観測できて
いないため、開始・主要境界・終端の direct playback は人間レビューに残る。

ここまでで delivery/access の機械条件は満たしたが、候補が一本の編集単位と
して自然かは未判断である。次に尋ねるのは次の一問だけとする。

> 追加Shorts候補ごとに、一本の編集単位として成立するか、テンポ・境界・字幕・音声に違和感があれば自由記述してください。

rights は `pending`。production render、production subtitle design、public、
publishing、upload は false / unopened のままで、この review は開かない。

## 次の端末での再開

```powershell
git fetch --prune origin
git switch codex/out-08-real-unused-range-short-minibatch-v0
git pull --ff-only
```

その後は `docs/RUNTIME_STATE.md`、この handoff、
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md` の順に読み、
localhost page を開く。server が止まっている場合だけ `review_open_command`
を使う。`artifacts/ACTIVE_REBUILD.json` は parked OUT-07 predecessor の
rebuild contract であって、OUT-08 の active readback ではない。

意図的に触れていないのは、ignored `episodes/` の追跡化、OUT-07 の追加調整、
caption/cut authority の変更、thumbnail 選定、rights/public/production/
publishing gate である。
