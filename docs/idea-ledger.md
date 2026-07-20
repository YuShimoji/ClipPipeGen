---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-21
---

# Idea Ledger - ClipPipeGen

OUT-08/09とSOURCE-04はexact candidateを`accepted_internal`として保持し、OUT-10とSOURCE-05は
bounded repair後の人間レビュー待ちである。ここでは、現在の判断を飛び越えずに別のbottleneckを
解く入口だけを保持する。proposalを実装済み・承認済み状態へ自動昇格させない。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: accepted context保持 | OUT-08/09/SOURCE-04の判断を再利用し、再レビュー摩擦を増やさない | exact SHAとreceiptを不変にする | 完了。SOURCE-04 MP4はcombined packageへ再copyしない | Agent: lineage維持 |
| G1: OUT-10 / SOURCE-05 repair review | 終端欠陥を直した新bytesの意味的自然さを確定 | 同じページで二本を一度確認し候補別自由記述 | `human_review_pending`、winnerなし | Human owner: accept / 違和感 / rejectを返す。Agent: exact SHAへbind |
| G2: OUT-10 / OUT-11 closure順 | branch差分を安全にmainへ統合可能な単位へ閉じる | G1で二本accept、tracked tests green、監修承認 | 未開始 | Supervisor/User: OUT-10先、OUT-11後の順序を承認。Agent: ff-only計画 |
| G3: 5-source failure taxonomy | source固有のmatte/crop/caption/text保持と一般化可能な規則を分ける | G1完了、5-source scorecard、人間結果 | 比較証拠あり、共通policy未選定 | Agent: speaker/歌詞推測なしで差分表。Human: 一般化対象を選ぶ |
| G4: production subtitle/render gate | internal candidateからproduction品質へ進む証拠不足を閉じる | G3、明示production slice、exact acceptance question | production acceptance false | Human owner: subtitle designとrenderを別々に判断 |
| G5: rights/material-use clearance | 技術成功と利用許可を接続する | source identity、rights owner、利用条件・制限 | `rights=pending` | Rights owner: 判断。Agent: receipt/readbackだけ更新 |
| G6: thumbnail system revisit | OUT-07一例を複数sourceで比較し偶然でないcover contractを作る | accepted portfolio、複数方向、独立thumbnail review | OUT-07は`PARK_PROVISIONAL_USABLE` | Supervisor/User: 再開判断。Agent: canonical化前に比較 |
| G7: private/unlisted delivery | 承認済みcandidateをrollback付きで外部deliveryへ渡す | G4/G5/G6の必要gate、OAuth/credentialsの別承認 | YouTube integration未実装 | Supervisor/User: scope承認。Agent: metadata/upload/visibilityを分離 |
| G8: portable artifact strategy | 別端末で同じmedia reviewを再現し手作業探索を減らす | private storage、transport、retention、rollback方針 | Gitはcode/docsのみ。mediaはsame-machine | Human owner: private artifact方針を承認。Agent:承認後に実装提案 |
| G9: operator cockpit end-to-end | source intakeからreview/decision/deliveryまで一つの再開面にする | G1〜G8の安定contract | read-only/action GUIとCLIが点在 | Agent: consumer-first vertical sliceを提案 |

## 次の取っ掛かり

- **Advance**: 修復二本を一度だけ見て候補別の自由記述を返す。OUT-10/11 closure計画へ進む唯一の
  直接入口。
- **Verify**: SOURCE-05に具体的違和感がある場合、時点とaudio/visual/endpointのどれかを示す。
  同じrecording内の再修復かpark/rejectを、歌詞推定なしで選べる。
- **Audit**: 二本受理後に5-sourceの字幕・構図差を比較する。internal acceptanceをproduction
  subtitle designへ広げず、source固有処理の誤一般化を防ぐ。
- **Explore**: cross-machine media reviewが必要ならprivate artifact戦略を別sliceで設計する。
  `episodes/`をGit追跡する案は、明示承認なしには採らない。

rights、production render/subtitle/image quality、thumbnail、winner、public/publishing、
upload/OAuth/visibility/made-for-kidsは、現在のhuman review pendingから開かない。
