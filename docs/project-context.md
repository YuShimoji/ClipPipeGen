---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-27
current_slice: OUT-14
phase: exact_v3_artifact_human_editorial_review_pending
active_branch: codex/out14-editorial-presentation-v3
source_branch: codex/out14-push-microarc-editorial-v2
verified_implementation_head: refs/heads/codex/out14-editorial-presentation-v3
sync_baseline_head: fab5d5a3369fe4d5defab265fa715201c3f8b0cf
base_main_head: edb782acd1e06aca46e0a5d10295ea52f30ad5c7
upstream_parity: not_configured_local_only
health: OUT14_EDITORIAL_V3_READY_FOR_HUMAN_REVIEW
---

# Project Context - ClipPipeGen

## 2026-07-27 現在の軸

exact v2 human reviewはsubtitle perceptual timing improvementだけを認め、
thumbnail、speaker-role presentation、laughter、material transition、
source-anchored explanationへbounded repairを要求した。v2 bytesとtechnical evidenceを
不変に保ち、`codex/out14-editorial-presentation-v3`で
`clip-out14-push-microarc-editorial-v3-001`を構築した。

生成前design basisとpredeclared direction signatureは
`docs/research/OUT14_EDITORIAL_V3_DESIGN_BASIS.md`に固定済み。
public example観測は4チャンネル・9本、fresh temporary signed-out profileで完了し、
競合surfaceを保存していない。role-aware subtitle、quote/laughter ledger、
8-boundary transition map、thumbnail再構成、probe、full render、全編self-reviewを接続し、
初回全編読戻しで見つけた同型分節を42境界の原因層修復へ戻した。正式再render後の
406.55秒全編再生はendedまで完走し、final SHAは
`fddae5a6688671ad301b1c1dcecd978a50865dd1fb5d678a6d55db1f3c18e9be`。

成功してもstateは`OUT14_EDITORIAL_V3_READY_FOR_HUMAN_REVIEW`。
human editorial、rights、YPP、production、publication、thumbnail acceptance、
upload、visibilityはclosed gateのまま。

## v2保存状態

OUT-14 v1はtechnical passを保存したままhuman editorial rejectとなった。
current artifactはv2
`clip-out14-push-microarc-editorial-v2-001`、final SHA
`8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414`。
3 stream / 9 candidateのselectorからDiscordプロフィール通知episodeを選び、
actual-audio transcript、8 cut、4 telop、title 3案、actual-frame thumbnail rough、
full media validation、localhost reviewまで接続した。

v2時点のbottleneckはexact v2 human reviewだった。現在のbottleneckはexact v3全体の
編集品質と言語精度、title / thumbnail promise、残存重大問題についてのhuman verdict。
rights readinessやproductionへは進んでいない。
v1 quarantine、v2 technical evidence、human decision、rights/production/public gateを
別identityで管理する。

詳細は`docs/CURRENT_HANDOFF.md`と`docs/SUPERVISOR_STATUS_REPORT.md`。

## OUT-13までの既存軸

### OUT-13時点の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。OUT-12で取得済み実sourceから
検証済み長尺MP4までの一コマンド経路を成立させ、OUT-13では明示的な
caption/transcript evidence付きeditorial planを、非連続cut、字幕、実MP4、
review packageへ運ぶ後継経路を追加した。

accepted feature branchは`codex/out-13-editorial-video-candidate-v1`、exact revisionは
`18641fe917b084259869263e8db05d78325aa2db`。start main
`5d6f69a64d510508a1f78ab3111a7780913a019c`から15 commitを
fast-forwardし、M4 main integrationを完了した。squash、merge commit、force、
履歴改変はなく、現在のactive branchは`main`である。

exact candidate 005の内部全編editorial / visual acceptanceは継承したまま、
integrated main treeでconfigured full Python suite、focused OUT-13 / acceptance /
semantic authority / dashboard、GUI/CLI smoke、compile/static、diff/privacy境界を確認し、
M5 integrated baseline verificationをpassした。current bottleneckは重複reviewや
main integrationではなく、M6 rights readinessのscopeと判断ownerを整理することである。

## 最近閉じたことと現在の停止点

| slice | 閉じた範囲 | 残っている境界 |
|---|---|---|
| OUT-10 / OUT-11 | five-source Shortをexact bytesへbindしてaccepted internal、winnerなし | universal visual policy、rights、production/public |
| OUT-12 | source→Timeline IR→MP4→validation→review→resumeをinternal operational化 | second-source long-form repeatability、production/public |
| OUT-13 | explicit plan、provider caption evidence、candidate 005 acceptance、M4 main integration、M5 baseline verification | rights/production |

current identityは`clip-out13-editorial-video-candidate-v1-005`。7 cuts / 5 sections /
8 omissions、final SHA`a76babda...bbb5`、25 files / 87,123,995 bytes、
package-tree digest`ed45fd4c...040`。source / transcript / caption / rights / planの
current hashesはtracked contractと一致し、`--resume`はrenderなし・5 cache hits・
package digest不変で成功した。review serverはpage 200 / MP4 Range 206を確認後に停止した。

artifact recovery、M2 human editorial acceptance、M3 readiness、M4 main integration、
M5 integrated baseline verificationは完了済み。受領receiptは
`docs/output_layer/out13_human_acceptance_receipt.json`。同じmedia SHA・review context・
accepted dimensionsを再reviewへ戻さず、次はM6 rights readinessだけを準備する。

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

完了したcritical pathは
`M3 branch preflight -> explicit integration authorization -> M4 integration -> M5 verification`。
将来repairが必要な場合だけ、変更・因果影響のあるdimensionとtimestampを限定して再確認する。

次はrights decision packetの準備条件を整理し、その後production subtitle design、
production render profileを
独立gateとして閉じ、episode acceptance packへ集約する。thumbnail / metadata /
private delivery / public releaseはその後に接続する。複数episode運用、品質学習、
policy-constrained autonomy、持続可能なproduction platformまでの長期段階とexit evidenceは
`docs/SUPERVISOR_STATUS_REPORT.md`を正本とする。

## 別端末での最短確認

```powershell
git fetch --prune origin
git switch main
git pull --ff-only origin main
git status --short --branch
git rev-list --left-right --count 'HEAD...@{upstream}'
git merge-base --is-ancestor 18641fe917b084259869263e8db05d78325aa2db HEAD
git ls-files episodes
```

期待値はmain parity`0 0`、accepted feature ancestry pass、tracked`episodes/` 0件。
その後にcandidate path、
inputs、plan、package、MP4を`Test-Path` / SHAでlive判定する。package不在の端末では
launcherを利用可能と報告しない。
