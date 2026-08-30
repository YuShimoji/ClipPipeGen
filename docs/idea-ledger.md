---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-08-30
---

# Idea Ledger - ClipPipeGen

旧「全体採用 / bounded revision」ゲートは設定不良としてレガシー化した。現在のWiki添削familyは、
335.3秒fixtureを全体採否せず、部分観察と独立作業を並行しながらEpisode統合へ進む。以下の入口は
同じ`ED-13R-*` task identityでCockpitとFrontierBoardへ投影し、別gateを混ぜない。

| 入口 | 解くbottleneck | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| Temporary task surface | 全体採否ゲートがProjectを止める | correction receipt、10 task IDs | active | CockpitとFrontierBoardを同じtask identityで読む |
| Partial observation | 長尺動画の局所的な気づきを残す | exact MP4 SHA、任意のoutput range | planned | 採否ではなく観察・不確実性・任意修正案を記録する |
| Optional navigation | 335秒を迷わず移動する | 既存8 navigation partitions | planned | 承認単位や質問にせず表示anchorだけを追加する |
| Workflow readback | legacy gateを前提にした状態表示 | rejection receipt | planned | DecisionCaseとartifact readbackを非blocking化する |
| Episode 1 integrated cut | CU-01→CU-02→CU-03を一続きにする | `Ocqg-RpQURY` 390–585秒exact media + receipt | exact-source blocked | bytes供給後preflightを再実行 |
| Rights / production | 利用・delivery品質を決める | selected material、owner verdict | closed | semantic/technical結果から開かない |

## 採らない方向

- 4本のproofをsemantic winnerやfinished Episodeとして数えない。
- fixed 25秒probe、coverage 0 overlap、decode PASSだけをcontent progressに変換しない。
- CU-02の代わりにretained sourceやcaption-only映像を差し込まない。
- `file://`不調を繰り返さず、同梱loopback serverのHTTP Range routeを使う。
- Gitにignored mediaを追加せず、許可された外部packetでだけtransportする。

## 次の取っ掛かり

- **Advance**: `ED-13R-03`〜`08`を順に進め、判断待ちではないProject作業を閉じる。
- **Review**: 必要な区間だけを開き、採否ではなく観察・不確実性・任意修正案を残す。
- **Verify**: 別端末でZIP外manifest、ZIP member closure、HTTP 200 / Range 206を再確認する。
- **Unblock**: Episode 1用CU-02 exact source bytesとreceiptを明示供給する。
