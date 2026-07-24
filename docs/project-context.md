---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-24
current_slice: OUT-13
phase: local_artifact_recovery_or_rebuild_required
active_branch: codex/out-13-editorial-video-candidate-v1
source_branch: codex/out-13-editorial-video-candidate-v1
verified_implementation_head: this_commit_after_push
sync_baseline_head: 602ab50240bbc8cf8899314679a268942834412d
base_main_head: 5d6f69a64d510508a1f78ab3111a7780913a019c
remote_handoff_tip: this_commit_after_push
upstream_parity: 0 0
health: OUT13_CODE_READY_LOCAL_REVIEW_ARTIFACT_RECOVERY_REQUIRED_V1
---

# Project Context - ClipPipeGen

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。OUT-12で取得済み実sourceから
検証済み長尺MP4までの一コマンド経路を成立させ、OUT-13では明示的な
caption/transcript evidence付きeditorial planを、非連続cut、字幕、実MP4、
review packageへ運ぶ後継経路を追加した。

active branchは`codex/out-13-editorial-video-candidate-v1`。
2026-07-24にremote tip`602ab50`でfetch / ff-only pullし、upstream parity`0 0`、
同期基準の`origin/main...HEAD = 0 11`を確認した。`origin/main`はHEADの祖先だが、
OUT-13側11 commitはmain未統合である。本context更新commitをpushした後のresume topologyは
upstream parity`0 0`、`origin/main...HEAD = 0 12`。
Node / Electron / CLI smokeとPython full suiteはgreenで、tracked実装は開発継続可能。

## 最近閉じたことと、現在の停止点

| slice | 閉じた範囲 | 残っている境界 |
|---|---|---|
| OUT-10 / OUT-11 | five-source Shortをexact bytesへbindしてaccepted internal、winnerなし | universal visual policy、rights、production/public |
| OUT-12 | source→Timeline IR→MP4→validation→review→resumeをinternal operational化 | second-source long-form repeatability、production/public |
| OUT-13 | explicit plan、provider caption evidence、immutable package、signed PCM lineage、review builder | local review artifact recovery、human verdict、main統合、rights/production |

source-host receipt上の最新identityは
`clip-out13-editorial-video-candidate-v1-005`。7 cuts / 5 sections / 8 omissions、
final SHA`a76babda...bbb5`を記録する。ただしcurrent host`DESKTOP-U9P4LKJ`には
candidate 004 / 005 package、plan、MP4、launcherがない。

現在のlocal source / transcript / rights hashは005契約と異なり、provider JSON3だけ一致する。
このためhuman review入口はcurrent surfaceから外した。005を復元済みと扱わず、
private recoveryまたは006以降のnew identity rebuildを先に行う。

## 再開時に読む順序

1. `AGENTS.md`
2. `README.md`
3. `docs/RUNTIME_STATE.md`
4. `docs/INVARIANTS.md`
5. `docs/AUTOMATION_BOUNDARY.md`
6. `docs/CURRENT_HANDOFF.md`
7. `docs/SUPERVISOR_STATUS_REPORT.md`

source-hostのmachine receiptは
`docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md`で参照する。
receiptの存在をcurrent filesystem上のartifact実在と混同しない。

## 守る境界

- `episodes/`はignoredかつtracked 0件を維持する。
- protected R3 `human_preview_session`をcleanupしない。
- candidate 004 / 005を上書きしない。
- NLMYTGenを含む他repositoryのfileを読まない・書かない。
- rights、production subtitle/design/render、thumbnail、public/publishing/uploadを
  machine validationから推定しない。
- credentials / OAuth / visibility変更は別sliceと明示承認なしに実行しない。

## 次の依存順

最短critical pathは
`artifact recoveryまたはnew identity rebuild -> exact SHA human editorial verdict ->
branch acceptance -> main integration`。

その後、rights decision packet、production subtitle design、production render profileを
独立gateとして閉じ、episode acceptance packへ集約する。thumbnail / metadata /
private delivery / public releaseはその後に接続する。長期段階とexit evidenceは
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

期待値はbranch parity`0 0`、tracked`episodes/` 0件。
その後にcandidate pathとinputsを`Test-Path` / SHAでlive判定する。
package不在の端末ではlauncherを利用可能と報告しない。
