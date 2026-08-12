---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-08-12
---

# Idea Ledger - ClipPipeGen

現在のWiki添削familyは、probe数やcoverageを増やす段階ではなく、同じsource/cut/subtitle/test
identity上で意味を選び、Episodeへ統合する段階である。以下の候補は別gateを混ぜない。

| 入口 | 解くbottleneck | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| Review proof set | openingとendpointの意味判断 | portable packet、loopback review、exact MP4 SHA | ready | human/editorがsemantic routeを選ぶかbounded repairを返す |
| Subtitle bounded repair | timing・改行・可読性の局所問題 | 選択routeと具体的な観察 | conditional | material/cutを変えずnew identityで修復 |
| Causal successor | source/cut/subtitle/testを一つの編集単位へ上げる | semantic route verdict | blocked on verdict | 採用された次元だけrender-ready inputへ反映 |
| Parent full-1x | 338.166016秒全体の知覚評価 | queued human review | queued | short proofで代替せず別gateのまま実施 |
| Episode 1 integrated cut | CU-01→CU-02→CU-03を一続きにする | `Ocqg-RpQURY` 390–585秒exact media + receipt | exact-source blocked | bytes供給後preflightを再実行 |
| Rights / production | 利用・delivery品質を決める | selected material、owner verdict | closed | semantic/technical結果から開かない |

## 採らない方向

- 4本のproofをsemantic winnerやfinished Episodeとして数えない。
- fixed 25秒probe、coverage 0 overlap、decode PASSだけをcontent progressに変換しない。
- CU-02の代わりにretained sourceやcaption-only映像を差し込まない。
- `file://`不調を繰り返さず、同梱loopback serverのHTTP Range routeを使う。
- Gitにignored mediaを追加せず、許可された外部packetでだけtransportする。

## 次の取っ掛かり

- **Review**: portable proofをtimestamp jumpで比較し、openingとendpointの二判断を返す。
- **Advance**: verdict後、選択次元だけをnon-overwriting causal successorへ反映する。
- **Verify**: 別端末でZIP外manifest、ZIP member closure、HTTP 200 / Range 206を再確認する。
- **Unblock**: Episode 1用CU-02 exact source bytesとreceiptを明示供給する。
