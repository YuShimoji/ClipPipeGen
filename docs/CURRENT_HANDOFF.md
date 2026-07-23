---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT13_EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1
progress_pct: 100
last_touched: 2026-07-23
current_slice: OUT-13
phase: internal_editorial_review_recovery_required
canonical_status: editorial_representative_video_reviewable_v1
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
base_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
sync_baseline_head: 558f681b3778b1b9bf43f6ec72b38768e8e3da44
verified_implementation_head: c1566b359413e4fbd5034733ac41d03d17641aaa
remote_resume_contract: fetch_then_switch_codex_out_13_branch_then_read_this_file
current_title: OUT-13 code green, exact local review artifact recovery required
human_entrypoint: null
portable_entrypoint: null
review_open_command: null
review_server_restart_command: null
machine_readback: null
decision_required: choose_exact_artifact_recovery_or_new_identity_rebuild_before_editorial_review
review_status: source_host_machine_validated_local_review_blocked_missing_exact_artifact
remote_code_complete: true
local_artifact_available: false
local_artifact_role: absent_current_checkout_historical_source_host_receipt_only
portable_local_artifact_available: false
cross_machine_resume_class: tracked_code_docs_only_out13_exact_inputs_plan_and_output_absent
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
next_action: recover_exact_out13_package_and_matching_inputs_or_build_explicit_new_identity_then_run_human_editorial_review
active_artifact: clip-out13-editorial-video-candidate-v1-001
remote_handoff_tip: this_commit_after_push
source_of_truth: true
owner_lane: editorial_real_video_internal_review
related: docs/RUNTIME_STATE.md, docs/SUPERVISOR_STATUS_REPORT.md, docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md, artifacts/ARTIFACTS.md, docs/AUTOMATION_BOUNDARY.md
upstream_parity: 0 0
---

# Current Handoff - ClipPipeGen

## 現在地

OUT-13は、hash-boundな明示editorial planからcaption/transcript evidenceを持つ6つの非連続cutを
時系列どおりに接続し、字幕付き実MP4、19項目validation、video-first review packageまで生成する
実装である。source-host receiptは4 sections / 122.866016s、final SHA
`84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2`、
公式JA 77 cue、Keifont 100px、最大2行、machine checks passを記録する。

active branchは`codex/out-13-editorial-video-candidate-v1`。2026-07-23にremote最新`558f681`へ
ff-only同期し、同期時upstream parityは`0 0`、`main` / `origin/main`は`5d6f69a`で一致した。
606 Python tests、Node/Electron smoke、OUT-13 CLI helpはpassしており、tracked codeの開発は可能。
OUT-13はmainへ未mergeで、人間の編集受理、rights、production/public gateも未承認である。

## source-host receiptとこのcheckoutを分ける

| 面 | tracked source-host receipt | current checkout | 再開上の意味 |
|---|---|---|---|
| source | SHA `e2206cef...2d18` | SHA `6f78657e...6103a` | bytes不一致 |
| transcript | SHA `ef928d4e...b42d6` | SHA `4a7b4fd8...3495` | bytes不一致 |
| official JA caption | SHA `3c15535f...d169919` | 同じSHA | 一致 |
| rights snapshot | SHA `e6ea9471...64c12` | SHA `4302c4a1...bb8` | bytes不一致 |
| editorial plan input | 11,333 bytes、documented SHA `75289fba...cb2b` | 不在 | original fingerprintを再現できない |
| final/review package | 25 files / 78,180,658 bytes、final SHA `84ed7aa6...791d7e2` | directoryごと不在 | review/HTTP/resume不可 |

repository rootと配下worktreeを対象に、`editorial_plan_input.json`、OUT-13 directory、final MP4、
readback、launcherを探索したが見つからなかった。source identity名が同じでも、SHA不一致を同一inputと
扱わない。source-hostの0.281s resume、page 200、Range 206はhistorical receiptであり、このcheckoutの
live resultではない。

## 開発環境と保持したlocal state

| 面 | 2026-07-23 live result |
|---|---|
| Git | sync baseline `558f681`; upstream parity `0 0`; mainとの差 `0 4` |
| Node | 24.13.0 / npm 11.6.2 / Electron 42.0.0 |
| npm | `npm ci`成功、24 packages audit、脆弱性0 |
| Python | CPython 3.13.3 / uv 0.10.7 / Pillow 12.3.0 |
| tests | final `uvx --with Pillow pytest -q` → 606 passed / 68.84s |
| smoke | `npm run smoke`、`npm run smoke:electron`、OUT-13 CLI help pass |
| media | FFmpeg/ffprobe 8.0.1 / yt-dlp 2026.03.17 |
| hygiene | `episodes/` 933 local files / tracked 0; R3 protected preview 28 files / 33,712,427 bytes |
| predecessor | OUT-12 final SHA `5d391ffd...a584` live一致 |

ignored `episodes/`、`.serena`、cache、他worktreeは削除していない。broad ignored cleanupは行わない。

## reviewを再開する前の二経路

1. **Exact recovery** — original packageとcontract-matching source/transcript/caption/rights/planを、
   生成hostまたは承認済みprivate transportから回収し、manifest/final hashを照合する。
2. **New-identity rebuild** — exact packageを回収しない場合、currentまたは再取得inputへ新しい
   editorial planをbindし、新artifact ID、input fingerprint、final SHA、旧receiptへのlineageを持たせる。

どちらの経路でも、reviewable bytesが揃うまでは`http://127.0.0.1:8076/`や旧launcherを案内しない。
new buildを旧SHAの復元と呼ばない。

## 別端末での再開

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

期待値はactive branch parity `0 0`、tracked `episodes/` 0件。次に
`docs/SUPERVISOR_STATUS_REPORT.md`を読み、OUT-13 pathと各input SHAをlive確認する。
Gitでportableなのはbuilder、tests、docs、source-host receiptまでであり、ignored mediaは別cloneへ届かない。

## 次の判断

最短critical pathは`artifact identity recovery -> human editorial review -> bounded repair（必要時） ->
main integration -> rights / production subtitle / production renderの個別gate`。現時点のowner判断は、
original exact packageを回収するか、旧identityと混同しないsuccessor rebuildへ進むかである。
thumbnail、publishing、uploadは後続consumerであり、現在のrecovery gateと一括で開かない。
