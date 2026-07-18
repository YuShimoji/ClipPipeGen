---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-19
---

# Idea Ledger - ClipPipeGen

OUT-09はexact SHA `b6b90a4b...73da50`を`accepted_internal`として閉じた。ここでは次に
進められる高シグナルの入口だけを保持し、proposalを承認済み実装と混同しない。主経路は
第三sourceを加えて比較可能なportfolioを作り、production/public gateを一つずつ開くことである。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: OUT-09 canonical closure | exact user acceptance、媒体identity、回帰比較をmainへ統合 | exact SHA、base-vs-branch、targeted tests、ff-only | 完了。`accepted_internal`、source-specific suppressionは非一般化 | Agent: canonical mainを維持 |
| G1: OUT-10 third-source portfolio expansion | 単一caption方式への過適合を減らし、三つ目のsourceで比較軸を作る | explicit slice approval、distinct source、12〜60秒、9:16、共通schema | `OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION` data-only / 未実装 | Supervisor/User: sourceと実装を承認。Agent: 承認後に最低1本生成 |
| G2: 3〜5本 portfolio / failure taxonomy | caption authority、crop/matte/blur、cue密度、解像度、render時間、人間結果をsource横断で比較 | G1成功、合計3〜5本のreal Shorts evidence | proposal | Agent: source別scorecardと失敗分類を提案。Supervisor: 一般化してよい規則だけを選ぶ |
| G3: output/subtitle limitation lift | internal acceptanceからproduction render・subtitle designへ進むための欠落証拠を閉じる | G2で再現性、明示的production slice、exact acceptance question | production acceptanceはfalse | Supervisor/User: gateを限定。Agent: render pathと字幕designを別々に検証 |
| G4: rights/material-use clearance | 一つの候補をproduction検討可能にし、技術成功と利用許可を接続する | source identity、rights判断owner、利用条件・制限の明示 | `rights=pending` | Human rights owner: 判断。Agent: readback/receiptを更新し、他gateを推測で開かない |
| G5: thumbnail system revisit | OUT-07の一例を3〜5本の実例と比較し、偶然でないcover選択contractを作る | G2 portfolio、複数比較方向、独立したthumbnail review | OUT-07は`PARK_PROVISIONAL_USABLE`、追加iteration禁止 | Supervisor/User: 再開判断。Agent: canonical化前に比較とlineageを証明 |
| G6: private/unlisted delivery integration | approved candidateを安全なvisibility既定値、dry-run、receipt、rollback付きで外部deliveryへ渡す | G3・G4・G5の必要gate、OAuth/credentials/paymentの別承認 | PB/YouTube integrationは未実装 | Supervisor/User: private/unlisted scopeを承認。Agent: metadata、upload、thumbnail、visibilityを分離実装 |
| G7: operator cockpit end-to-end | source intakeからreview/decision/deliveryまでをGUI/CLIで再開可能にし、手作業のartifact探索を減らす | 安定したG1〜G6 contract、episode_pack、portable/private artifact方針 | read-only/action GUIと各CLIは点在、完全統合は未実装 | Agent: consumer-first vertical sliceを提案。Human: destructive/public actionだけ明示確認 |
| G8: repeatable multi-episode production-assist loop | 複数source・複数episodeでtraceable artifact、判断receipt、rollback、公開handoffを再現する | G7、運用metrics、retention/privacy、rights/public acceptance model | 長期north-star proposal | Supervisor: KPIとstop条件を定義。Agent: 公開判断を自動化せず、判断材料と実行境界を接着 |

## 近い代替入口

- **Advance**: OUT-10を承認し、第三sourceでpipeline再現性を直接検証する。最も
  product gapを縮める推奨経路。
- **Audit**: OUT-09のblur/mosaicを共通デザインへ誤一般化しない。OUT-10でcaption bandや
  crop conflict条件が変わった時だけ比較scorecardへ昇格する。
- **Explore**: parked recovery proofをepisode共通handoffへ一般化する。ただしprivate
  storage / transport / retention / rollback方針の明示承認がある場合だけで、OUT-08
  closure条件には戻さない。
- **Excise**: `RUNTIME_STATE.md`の長いhistorical sectionと
  `FEATURE_REGISTRY.md`のmojibakeを別docs-health sliceで整理する。current product
  decisionを変えず、one-pass re-entryの摩擦だけを下げる。

rights、production render、production subtitle design/image quality、thumbnail、public/
publishing、upload/OAuth/visibility/made-for-kidsは、OUT-09 internal acceptanceから開かない。
