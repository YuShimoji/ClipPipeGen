---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-25
current_slice: OUT-13
phase: human_editorial_review_pending
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
verified_implementation_head: this_commit_after_push
sync_baseline_head: 396432635710622f6573ae15e3f0537452a6c14f
base_main_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
remote_handoff_tip: this_commit_after_push
upstream_parity: 0 0
health: OUT13_LOCAL_EXACT_REVIEW_READY_HUMAN_EDITORIAL_DECISION_PENDING_V1
---

# Project Context - ClipPipeGen

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。OUT-12で取得済み実sourceから
検証済み長尺MP4までの一コマンド経路を成立させ、OUT-13では明示的な
caption/transcript evidence付きeditorial planを、非連続cut、字幕、実MP4、
review packageへ運ぶ後継経路を追加した。

active branchは`codex/out-13-editorial-video-candidate-v1`。
2026-07-25にremote tip`3964326`へff-only更新し、upstream parity`0 0`、
`origin/main...HEAD = 0 12`、`origin/main`がHEADの祖先であることを確認した。
OUT-13側12 commitはmain未統合で、このcontext更新commitをpushした後のresume topologyは
upstream parity`0 0`、`origin/main...HEAD = 0 13`になる。

Node依存、GUI / Electron / CLI、exact candidate 005 resume、localhost page / Range、
Python full suite 654 testsを使って開発再開性を確認した。tracked codeと同一マシンのreview targetの双方が
利用可能で、current bottleneckは人間の全編editorial verdictである。

## 最近閉じたことと現在の停止点

| slice | 閉じた範囲 | 残っている境界 |
|---|---|---|
| OUT-10 / OUT-11 | five-source Shortをexact bytesへbindしてaccepted internal、winnerなし | universal visual policy、rights、production/public |
| OUT-12 | source→Timeline IR→MP4→validation→review→resumeをinternal operational化 | second-source long-form repeatability、production/public |
| OUT-13 | explicit plan、provider caption evidence、immutable package、signed PCM lineage、review builder、candidate 005 exact local revalidation | human editorial verdict、main統合、rights/production |

current identityは`clip-out13-editorial-video-candidate-v1-005`。7 cuts / 5 sections /
8 omissions、final SHA`a76babda...bbb5`、25 files / 87,123,995 bytes、
package-tree digest`ed45fd4c...040`。source / transcript / caption / rights / planの
current hashesはtracked contractと一致し、`--resume`はrenderなし・5 cache hits・
package digest不変で成功した。review serverはpage 200 / MP4 Range 206を確認後に停止した。

artifact recoveryはcurrent hostでは完了済み。人間がexact SHAへ
`accept` / bounded `repair` / `reject`を記録するまでeditorial acceptanceはpending。

## 再開時に読む順序

1. `AGENTS.md`
2. `README.md`
3. `docs/RUNTIME_STATE.md`
4. `docs/INVARIANTS.md`
5. `docs/AUTOMATION_BOUNDARY.md`
6. `docs/CURRENT_HANDOFF.md`
7. `docs/SUPERVISOR_STATUS_REPORT.md`

candidate contractと実行経路は
`docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md`で確認する。
tracked receiptの存在だけで別hostのartifact実在を推定せず、毎回`Test-Path`とhashで照合する。

## 守る境界

- `episodes/`はignoredかつtracked 0件を維持する。
- protected R3 `human_preview_session`をcleanupしない。
- candidate 004 / 005を上書きしない。
- NLMYTGenを含む他repositoryのfileを読まない・書かない。
- rights、production subtitle/design/render、thumbnail、public/publishing/uploadを
  machine validationやhuman editorial acceptanceから推定しない。
- credentials / OAuth / visibility変更は別sliceと明示承認なしに実行しない。
- current hostの`local_artifact_available=true`をGit-only別hostへ自動継承しない。

## 次の依存順

最短critical pathは
`exact SHA human editorial verdict -> branch acceptance -> main integration`。
repairの場合だけ`bounded finding -> candidate 006+ -> exact SHA re-review`を挟む。

その後、rights decision packet、production subtitle design、production render profileを
独立gateとして閉じ、episode acceptance packへ集約する。thumbnail / metadata /
private delivery / public releaseはその後に接続する。複数episode運用、品質学習、
policy-constrained autonomy、持続可能なproduction platformまでの長期段階とexit evidenceは
`docs/SUPERVISOR_STATUS_REPORT.md`を正本とする。

## 別端末での最短確認

```powershell
git fetch --prune origin
git switch codex/out-13-editorial-video-candidate-v1
git pull --ff-only
git status --short --branch
git rev-list --left-right --count HEAD...origin/codex/out-13-editorial-video-candidate-v1
git ls-files episodes
```

期待値はbranch parity`0 0`、tracked`episodes/` 0件。その後にcandidate path、
inputs、plan、package、MP4を`Test-Path` / SHAでlive判定する。package不在の端末では
launcherを利用可能と報告しない。
