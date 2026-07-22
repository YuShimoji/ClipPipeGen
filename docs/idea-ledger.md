---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-22
---

# Idea Ledger - ClipPipeGen

OUT-10/11のShort portfolioはaccepted internal・winnerなしで閉じ、OUT-12の実長尺動画automationは
operationalになった。以下は別々のbottleneckを解く候補であり、proposalを実装済み・承認済みへ
自動昇格させない。rights、production、public gateは技術成功から推定しない。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: OUT-10/11 closure保持 | accepted Shortを再修復せず、比較authorityとして再利用 | exact SHAとreceiptを不変にする | 完了 | Agent: lineage維持 |
| G1: OUT-12 one-command real video | source→Timeline IR→MP4→validation→review→resumeを一縦糸にする | 取得済みreal source、FFmpeg/FFprobe | 完了。11 cuts / 260.693767s / SHA `5d391ffd...a584` | Agent: regression時だけ修復 |
| G2: second long-form source repeatability | SOURCE-05固有の偶然を除き、3分以上sourceで一般性を確かめる | distinct real source、3分以上、provenance、local storage | proposed | User/Supervisor: source laneを選択。Agent:同じCLIで実走 |
| G3: long-form failure taxonomy | AV sync、peak、black/silence、caption/native text、scene boundaryの修復規則を比較可能にする | G2または複数run evidence | initial evidenceあり、一般化未実施 | Agent: source-specificと共通validationを分離 |
| G4: production subtitle design | native baked textと追加字幕のproduction表示方針を決める | 明示production subtitle-design gate、human visual review | false | Human owner: design判断。Agent:exact artifactへbind |
| G5: production render acceptance | internal H.264/AAC plumbingからproduction output contractへ進む | G4、delivery spec、device/QC、exact acceptance | false | Supervisor/User: scope承認 |
| G6: rights/material-use clearance | 技術成功と利用許可を接続する | source identity、rights owner、利用条件・制限 | `rights=pending` | Rights owner:判断。Agent:receipt/readback更新 |
| G7: thumbnail system revisit | OUT-07一例を複数sourceで比較し、偶然でないcover contractを作る | 複数accepted output、独立thumbnail review | `PARK_PROVISIONAL_USABLE` | Supervisor/User:再開判断 |
| G8: private artifact transport | 別端末で同じsource/final MP4を安全に再生する | private storage、retention、access、rollback方針 | Gitはcode/docsのみ、media same-machine | Human owner: transport方針承認 |
| G9: private/unlisted delivery | accepted artifactをrollback付きで外部deliveryへ渡す | G4/G5/G6、OAuth/credentials別承認 | YouTube integration未実装 | Supervisor/User: metadata/upload/visibilityを分離承認 |
| G10: operator cockpit consolidation | source intakeからreview/decision/deliveryまで一再開面にする | G2〜G9の安定contract | CLI/dashboard/review pageは存在 | Agent: consumer-first thin sliceを提案 |
| G11: production candidate convergence | subtitle/render/rightsの独立receiptを一episode identityへ束ね、未承認面を一画面で判断可能にする | G4/G5/G6の個別acceptance、episode pack contract | long-range proposed | Supervisor: gate統合ではなくreceipt集約として承認 |
| G12: explicit public release decision | private/unlisted delivery後にだけpublic化を判断し、visibility等を監査可能にする | G7/G9/G11、最終human decision、rollback手順 | future gate | Human owner: public化の直前に明示判断 |
| G13: multi-episode operations | 単発artifactからqueue/retry/retention/quality trendを持つ継続運用へ進む | G2〜G12のcontract安定、複数episode evidence | long-range proposed | Agent:一episodeの失敗を隔離するthin orchestrationから提案 |

## 次の取っ掛かり

- **Advance**: distinctな3分以上sourceを一つ選び、同じ`build-real-video` routeを実走する。
  source固有実装を増やさずrepeatabilityを測れる。
- **Audit**: current OUT-12 artifactのcut/tempo/contentを任意確認する。これはautomation acceptanceを
  変更せず、次source選定やfailure taxonomyへの観測を増やす。
- **Verify**: rights、production subtitle design、production renderのうち一gateだけを開く。
  一括承認やpublic readinessへの飛躍はしない。
- **Explore**: cross-machine media reviewが必要ならprivate artifact strategyを先に決める。
  `episodes/`をGit追跡する案は採らない。

現在の必須decisionはない。未選択の案は`proposed`のまま保持する。
依存順と各段階の最小証拠は`docs/SUPERVISOR_STATUS_REPORT.md`のM0〜M8 goal ladderを参照する。
