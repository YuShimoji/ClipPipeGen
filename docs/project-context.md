---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-27
current_slice: ED-12
phase: s1_s3_probe_built_s4_human_review_pending
active_branch: codex/s1-two-source-common-context-probe-v1
base_main_revision: edb782acd1e06aca46e0a5d10295ea52f30ad5c7
implementation_revision: a3771bc59cd58b05c00a570e1074118ace3dc15a
sync_observed_head: 9656f58e55136c4d4a32f758d65484f9610c6feb
upstream_parity: 0 0
health: S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW
---

# Project Context - ClipPipeGen

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。OUT-12で一source長尺route、
OUT-13でcaption-evidence付き非連続editorial routeを成立させた。OUT-13 Candidate 005は
内部editorial受領後、public / monetized pathをdenyしてread-only archive evidenceになった。

現在のED-12 / S1は、OUT-13を公開候補へ戻す作業ではない。別identity
`clip-s1-two-source-common-context-probe-v1-001`へ、取得済み実source二本、direct caption
evidence、creator-authored thesis/commentary、range rights readbackを結び、一つの論として
レビューできるbounded successor probeを作る。

## 到達済みの停止点

| 項目 | 状態 | 何が可能になったか |
|---|---|---|
| remote baseline | `main` / `origin/main` = `edb782a` | 最新canonical deny状態を継承 |
| repository / implementation | `9656f58` / `a3771bc`、branchはmainより2 commit先、upstream parity 0 0 | CLI、renderer、tests、handoffを再開可能 |
| exact package | MP4 SHA `dc621bfe...f95be`、19 files | 同一マシンでS4全編review可能 |
| machine validation | 16/16 checks、focused 12、full 689 | code/packageの技術基線はgreen |
| human decision | pending | 二source共通文脈の意味判断が現在のbottleneck |
| rights / production / public | closed | 技術greenから許諾・公開を推定しない |

timelineは6 cut、各source 3 cut、5 source switches、98.896秒。caption 60 cueとcreator
commentary 3 eventを別provenance trackに置く。source内時系列、continuous output clock、
cut-to-source mappingを保持する。

## 最終成果物像

短期の完成像は、S4 verdictがexact MP4 SHAへbindされ、acceptなら内部two-source
argumentative-editing patternとして一例が閉じること。repairなら変えた次元だけをnew identityで
再確認すること。rejectなら、このpair/thesis/directionを再利用しないこと。

中長期の完成像は、複数sourceの意味的関係を証拠へ戻せる編集計画、明示rights判断、
production subtitle/render、episode acceptance、private delivery、明示public releaseまでを、
各ownerのreceiptを混ぜずに接続する制作系である。generic frameworkは二つ目の成功例と
一つの失敗例が揃うまで先に作らない。

## 現在の最大gap

machine validationは「正しく二本をrenderした」ことを示す。現在まだ示していないのは
「二本を交互に置くことで中心問いが深まり、commentaryが過剰説明になっていない」こと。
この意味判断がS4であり、コード追加より先に人間がexact artifactを評価する。

## 再開順

1. `AGENTS.md`
2. `README.md`
3. `docs/RUNTIME_STATE.md`
4. `docs/INVARIANTS.md`
5. `docs/AUTOMATION_BOUNDARY.md`
6. `docs/CURRENT_HANDOFF.md`
7. `docs/SUPERVISOR_STATUS_REPORT.md`
8. `docs/output_layer/S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md`

同一マシンではS1 package、manifest、MP4 SHAをlive照合する。別端末ではGitに含まれない
`episodes/`を利用可能と推定しない。

## 守る境界

- `episodes/`はignoredかつtracked 0件を維持する。
- protected R3 `human_preview_session`をcleanupしない。
- OUT-13 Candidate 003–005とS1 successful packageを上書きしない。
- NLMYTGenを含む他repositoryのfileを読まない・書かない。
- human S4 verdictをagentのsample frame観察やmachine validationで代替しない。
- rights、production subtitle/design/render、thumbnail、publishing、upload、public releaseを
  S4 editorial verdictから推定しない。
- credentials / OAuth / visibility変更は別sliceと明示承認なしに実行しない。

## 次の依存順

`S4 human common-context review -> S5 bounded closure -> S6 fresh rights inventory ->
S7 rights/publication decision -> S8 production design -> S9 delivery render ->
S10 episode acceptance`が近接critical path。second-pair repeatabilityとexternal deliveryは、
最初のS4/S5結果を踏まえて独立gateとして起票する。

長期exit evidenceと条件分岐は`docs/SUPERVISOR_STATUS_REPORT.md`を正本とする。
