---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-27
---

# Idea Ledger - ClipPipeGen

現在のbottleneckは`clip-out14-push-microarc-editorial-v3-001`のexact human review。
v1のtechnical success/editorial rejection、v2の限定acceptとpresentation reject、
v3の原因所有repairは別identityで保存済み。v3は4チャンネル・9本の生成前観測、
role-aware字幕、quote/laughter、8 cut grammar、source-anchored explanation、
thumbnail再構成、全編再生、bounded repairまで到達した。
次の価値は4本目を作ることではなく、このexact v3の人間判断を得てから、
今回の停止条件をmission-specific contractへ抽出することにある。

| 方向 | workflowへの効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| G2 exact v3 review | 全体編集、言語、title、thumbnail、重大問題を判断可能にする | exact SHAとlocalhost package | ready | Human: accept / bounded_repair / reject |
| G3 affected-only repair | 実欠陥だけを新SHAへ開き、受理済み範囲を反復しない | affected timestamp/dimension | conditional | Agent＋Human: 限定修復と再review |
| G4 internal editorial lock | exact mediaと受理dimensionを後工程へ固定 | G2 acceptまたはG3収束 | proposed | Human: SHA-bound receipt |
| G5 mission-specific contract | presentationの停止条件を再利用可能にする | G4 | proposed | Supervisor: schemaと停止条件を抽出 |
| G6 second accepted episode | 一回限りの成功かを判定 | G5最小contract | proposed | Agent: 別episodeでrepeat |
| G7 third episode/trend | repair率とquality driftを観測 | G6 pass | proposed | Supervisor: 3本比較 |
| G8 rights | 技術成果と利用可否を接続 | exact accepted artifact、owner/platform/territory | closed | Rights owner: receipt |
| G9 production subtitle/font | internal字幕をdelivery designへ上げる | G4、font/license | closed | Designer: device/safe-area receipt |
| G10 production render | delivery codec/audio/device QCを閉じる | G8/G9 | closed | Production owner |
| G11 title/thumb/metadata | creative promiseをexact videoへ固定 | final video lock | closed | Editorial owner |
| G12 private rehearsal | 公開前のauth/idempotency/rollbackを証明 | G8–G11、credential authority | closed | Account owner |
| G13 private delivery | remote object identityを確定 | G12 pass、明示承認 | closed | Account owner |
| G14 public release | 公開を監査可能にする | private proof、全owner approval | future gate | Human owner |
| G15 operations | queue/retry/retention/quality/costを扱う | 3+ accepted episode | long-range | Supervisor |
| G16 constrained autonomy | 自動停止・drift・budgetを運用する | G15 observations | long-range | Owner |

## 保留・棄却した方向

- v1を字幕だけ直して復活させる案。active quarantineはcosmetic repairを脱出条件にしない。
- funeral/deathをtitleやthumbnail主要hookにする案。sensitivity hard gateでreject。
- source countだけで`CATALOG_TOPIC_FEATURE`へ一般化する案。delivery intentとsource countは別軸。
- provider auto captionをviewer authorityにする案。provenanceとcanonical actual audioを分離する。
- 4本目のreal-topic render。3件の観測より先にcontract抽出とhuman verdictが必要。

## 次の取っ掛かり

- **Advance**: G2 exact v3 human review。現在の唯一の主要bottleneckを閉じる。
- **Audit**: 重大指摘がある場合だけtimestampとdimensionへ絞り、G3の影響範囲を閉じる。
- **Explore**: G4後にG5をsegmentation、role、transition、thumbnail、停止条件へ分解する。
- **Verify**: v3/v2 SHA、tracked episode 0、Git状態、HTTP 200/206をreview前に読戻す。

長期依存とowner境界は`docs/SUPERVISOR_STATUS_REPORT.md`を正本とする。
