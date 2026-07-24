# 監修AI向け現状報告 — 2026-07-24 OUT-13 candidate 005 remote handoff

更新日: 2026-07-24 JST

## いま再開できる地点

ローカルの tracked code/docs/tests は `codex/out-13-editorial-video-candidate-v1` にある。handoff開始時に
`git fetch --prune origin` と `git pull --ff-only origin codex/out-13-editorial-video-candidate-v1` を行い、
変更はなく、HEAD と upstream は `3fdad157c09cc925a50750135e14fff5faa832f2` で一致した。その後のdocs handoff commitが
この報告を含むremote resume tipである。worktree は clean、
`origin/main` は `5d6f69a64d510508a1f78ab3111a7780913a019c`、active branch は main より8 commit先である。
OUT-13をmainへmergeした事実はない。

このThank端末には、ignored local evidenceとして candidate 005 の exact review package も存在する。
従って現在の停止点は「artifact不在」ではなく、`machine validation/browser verification は完了、
human editorial review は未実施`である。別端末へGitだけをcloneしても`episodes/`は移らないため、
同じ映像を見せるには承認済みprivate transferでpackageとinputsを持ち込むか、new identityとして再生成する。

## 同期・衛生状態

| 確認面 | live result | workflow上の意味 |
|---|---|---|
| remote sync | fetch/prune後、対象branchのpullは `Already up to date` | remoteとlocalのbranch履歴を一致させた |
| parity | `git rev-list --left-right --count 'HEAD...@{upstream}'` → `0 0` | push待ちのtracked差分はない |
| worktree | `git status --short --branch` にbranch行のみ | 未コミットtracked変更なし |
| main topology | `origin/main...HEAD` → `0 8` | OUT-13は未mergeのactive review branch |
| artifact hygiene | `git ls-files episodes` → 0、candidate packageはignore対象 | private mediaをGitへ公開していない |

## candidate 005 の実体と機械検証

| 面 | 照合結果 | まだ意味しないこと |
|---|---|---|
| artifact identity | `clip-out13-editorial-video-candidate-v1-005`、state `OUT13_CANDIDATE_005_IMMUTABLE_TRANSITIVELY_LINEAGE_BOUND_REVIEWABLE_V1` | human受理済みではない |
| package | 25 files、87,123,995 bytes、tree digest `ed45fd4c...040` | 別端末へ自動portableではない |
| final media | 128.833333s、H.264 High/AAC、1920x1080、SHA `a76babda...bbb5` | production render / public-readyではない |
| content lineage | source/transcript/caption/rights/fontのauthority binding `passed`、source `youtube:7J5aS_pcBj4` | rights許可、speaker/歌詞の意味判断ではない |
| captions | provider JSON3 102 cues、overlap/negative/orphan/split/duplicate 0、mapping 1.0 | provider textの公式著者性を主張しない |
| audio/signal | `-14.48 LUFS`、`-1.88 dBTP`、最大隣接cut差 `1.85 LU`、black/silence event 0 | production mix承認ではない |
| validation | full decode、faststart、timestamp、A/V、caption boundary、mapping、closed manifest pass | browser QAを人間全編視聴へ昇格しない |
| browser surface | page 200、MP4 Range 206、横overflowなし、初期paused/muted、media warning/error 0 | editorial qualityの最終判断ではない |

packageの`visual_observation`は意図的に`unverified`、`human_review_pending=true`、
`editorial_acceptance_granted=false`である。候補005を人間が全編視聴し、編集構成・字幕表示・画面・音声について
`accept`、対象を限定した`repair`、または`reject`をfinal SHAへ記録するまで、acceptanceを代筆しない。
candidate 004はparallel review targetとして保持し、005の判断で上書きしない。

## この端末でのレビュー入口

まず `Test-Path episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\index.html`
が `True` であることを確認し、foreground PowerShellで次を実行する。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260723\review\out13_editorial_video_candidate_v005\review\open_preview.ps1
```

repairの場合は、cut ID・caption ID・timestamp・観察事実を先に記録し、candidate 004/005を上書きせず
006以降のsuccessor identityを作る。review serverを別端末へ移す場合は、server URLだけを引き継がず、
package treeと主要SHAを照合する。

## portable境界と未完了gate

Gitでportableなのはbuilder、tests、docs、schemas、CLI contractである。source MP4、transcript、caption、
rights snapshot、font bytes、editorial plan、final MP4、review images、launcherは`episodes/`配下の
ignored same-machine evidenceであり、Git cloneでは取得できない。

| gate | 現在 | 次に必要な証拠 |
|---|---|---|
| code / machine validation | 完了 | docs更新後もfull suiteとdiff checkを維持 |
| exact artifact access on Thank | 完了 | package pathとfinal SHAの再照合 |
| human editorial acceptance | 未完了 | candidate 005のSHA-bound accept/repair/reject |
| bounded repair | 条件付き | 人間がrepairを選んだときのみ、006以降を一回の限定修復として実施 |
| main integration | 未実施 | editorial closure後のmerge preflight、回帰、main parity |
| rights | pending | source/range/time/reviewer付きowner receipt |
| production subtitle/render | false | production仕様、font/license、device/color/audio QC、human receipt |
| thumbnail / publishing / upload / public | 未実装または未承認 | 別sliceと明示承認、credentials・visibility gate |

## 先へ進む順序

| 入口 | 解く摩擦 | 選択後に可能になること |
|---|---|---|
| **Review** | 既にあるexact bytesを人間判断へ接続する | acceptならintegration、repairならbounded successorへ進める |
| **Restore** | 別端末でignored packageが見えない | exact SHAを維持したcross-device reviewへ進める |
| **Rebuild** | private transferを選ばない場合の停止 | 新しいplan/input fingerprint/artifact IDでレビュー可能な候補を作る |
| **Audit** | acceptance後の修復・統合境界が曖昧になる | failure/resume/lineage条件を先に固められる |

推奨critical pathは `Review -> bounded repair if requested -> main integration -> rights / production gates`。
OUT-12の別source repeatability debtは残っているため、main統合後の独立監査としてdistinct 3分以上sourceで
同じlong-form routeを検証する。ただしそれをcandidate 005のhuman acceptanceやrights許可の代用にはしない。

## 意図的に触っていない範囲

NLMYTGenや他repository、他worktree、`.serena/`、credentials、保護中のhuman preview session、
`episodes/`内の生成media、main merge、rights判断、production/public操作には触れていない。Git上では
`docs/CURRENT_HANDOFF.md`、`docs/RUNTIME_STATE.md`、`docs/project-context.md`、本報告、
`docs/decision-log.md`、`docs/idea-ledger.md`を同期し、別端末が同じ境界から再開できるようにした。
