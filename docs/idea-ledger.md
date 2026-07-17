---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-17
---

# Idea Ledger - ClipPipeGen

OUT-08は`accepted_all_internal`で閉じた。ここでは次に進められる高シグナルの入口だけを
保持し、proposalを承認済み実装と混同しない。主経路は「sourceを増やして再現性を
証明してから、production/public gateを一つずつ開く」である。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: synchronized development baseline | remote・cockpit・live evidence・検証コマンドを一致させ、次agentが調査をやり直さず実装判断へ入れる | `main` parity、tracked clean、live readback、full test | 2026-07-17完了。`b3cec5d`、521 tests、GUI smokes pass | Agent: このbaselineを維持。Pillowは明示注入する |
| G1: OUT-09 second-source repeatability | 一つのsourceへの過適合を検出し、既存Shorts pipelineを別source/episodeで証明する | explicit slice approval、別source/episode、rights readback、大規模rewriteなし | `OUT09_SECOND_SOURCE_SHORT_REPEATABILITY` data-only proposal | Supervisor/User: 承認とsource方針を決める。Agent: 承認後、12〜60秒・9:16・reviewable candidateを最低1本作る |
| G2: 3〜5本 portfolio / failure taxonomy | 境界・字幕wrap・音量・再生性の再発をsource横断で計測し、偶然の成功と再現可能なcontractを分ける | G1成功、合計3〜5本のreal Shorts evidence | 未起票goal proposal | Agent: source別scorecardと失敗分類を提案。Supervisor: 一般化してよい規則だけを選ぶ |
| G3: output/subtitle limitation lift | diagnostic/internal acceptanceからproduction render・production subtitle designへ進むための欠落証拠を閉じる | G2で再現性、明示的production slice、exact acceptance question | 既存ED-10 limitation-lift資料はあるがproduction acceptanceはfalse | Supervisor/User: gateを開く対象を限定。Agent: render pathと字幕designを別々に検証 |
| G4: rights/material-use clearance | 一つの候補をproduction検討可能にし、技術成功と利用許可を接続する | source identity、rights判断owner、利用条件・制限の明示 | `rights=pending` | Human rights owner: 判断。Agent: readback/receiptを更新し、他gateを推測で開かない |
| G5: thumbnail system revisit | OUT-07の一例を3〜5本の実例と比較し、偶然でないcover選択contractを作る | G2 portfolio、複数比較方向、独立したthumbnail review | OUT-07は`PARK_PROVISIONAL_USABLE`、追加iteration禁止 | Supervisor/User: 再開判断。Agent: canonical化前に比較とlineageを証明 |
| G6: private/unlisted delivery integration | approved candidateを安全なvisibility既定値、dry-run、receipt、rollback付きで外部deliveryへ渡す | G3・G4・G5の必要gate、OAuth/credentials/paymentの別承認 | PB/YouTube integrationは未実装 | Supervisor/User: private/unlisted scopeを承認。Agent: metadata、upload、thumbnail、visibilityを分離実装 |
| G7: operator cockpit end-to-end | source intakeからreview/decision/deliveryまでをGUI/CLIで再開可能にし、手作業のartifact探索を減らす | 安定したG1〜G6 contract、episode_pack、portable/private artifact方針 | read-only/action GUIと各CLIは点在、完全統合は未実装 | Agent: consumer-first vertical sliceを提案。Human: destructive/public actionだけ明示確認 |
| G8: repeatable multi-episode production-assist loop | 複数source・複数episodeでtraceable artifact、判断receipt、rollback、公開handoffを再現する | G7、運用metrics、retention/privacy、rights/public acceptance model | 長期north-star proposal | Supervisor: KPIとstop条件を定義。Agent: 公開判断を自動化せず、判断材料と実行境界を接着 |

## 近い代替入口

- **Advance**: G1を承認し、別source/episodeでpipeline再現性を直接検証する。最も
  product gapを縮める推奨経路。
- **Audit**: `sub_067` / `sub_068`のexact-render受入を全動画共通規則へ誤一般化
  しない。G1で同種wrapが再発した時だけsource横断scorecardへ昇格する。
- **Explore**: parked recovery proofをepisode共通handoffへ一般化する。ただしprivate
  storage / transport / retention / rollback方針の明示承認がある場合だけで、OUT-08
  closure条件には戻さない。
- **Excise**: `RUNTIME_STATE.md`の長いhistorical sectionと
  `FEATURE_REGISTRY.md`のmojibakeを別docs-health sliceで整理する。current product
  decisionを変えず、one-pass re-entryの摩擦だけを下げる。

rights、production render、production subtitle design、thumbnail、public/publishing、
upload/OAuth/visibility/made-for-kidsは、OUT-08 internal acceptanceから自動的に開かない。
