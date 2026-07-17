---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-17
---

# Idea Ledger - ClipPipeGen

OUT-08は`accepted_all_internal`で閉じた。ここでは次に進められる高シグナルの入口だけを
保持し、proposalを承認済み実装と混同しない。

| 入口 | 目的 / 効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| Advance: OUT-09 second-source repeatability | 一つのsourceへの過適合を検出し、既存Shorts pipelineの再現性を証明する | 別sourceまたはepisode、rights readback、既存pipelineを大規模改変しないslice承認 | `OUT09_SECOND_SOURCE_SHORT_REPEATABILITY` data-only proposal | 12〜60秒・9:16・reviewable candidateを最低1本作る実行contractを、承認後に起票 |
| Audit: accepted subtitle debt | `sub_067` / `sub_068`のexact-render受入を全動画共通規則へ誤一般化しない | OUT-09で同種wrap問題が再発、またはproduction subtitle design gateが開く | exact OUT-08内だけaccepted | 再発時にsource横断scorecardを作り、字幕規則のsuccessorを別sliceで判断 |
| Explore: optional artifact portability | parked recovery proofをepisode共通handoffへ一般化できるか評価する | private storage / transport / retention / rollback方針の明示承認 | recovery branch `d1f44d1`をoptional noncanonical proofとしてremote保持 | 承認がある場合だけSH-02 successor contractを提案。OUT-08 closure条件には戻さない |
| Defer: OUT-07 thumbnail iteration | 一例の成功をcanonical design ruleにしない | real Shortsが合計3〜5本、別途thumbnail判断 | `PARK_PROVISIONAL_USABLE` | OUT-09等でportfolioを増やしてから再開可否を審査 |

rights、production render、production subtitle design、thumbnail、public/publishing、
upload/OAuth/visibility/made-for-kidsは、OUT-08 internal acceptanceから自動的に開かない。
