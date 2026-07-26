---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-27
---

# Idea Ledger - ClipPipeGen

現在のbottleneckは`clip-out14-push-microarc-editorial-v2-001`のexact human review。
v1のtechnical successとeditorial rejectionは分離して保存済みで、v2は別episode、
actual-audio transcript、可視構成、title/thumbnail roughまで進んだ。
次の価値は4本目を作ることではなく、v2の人間判断を得て再利用可能な
Factory Contract v2へ抽出することにある。

| 方向 | workflowへの効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| G4 exact review | v2の構成・字幕・telop・title・roughを判断可能にする | exact SHAとlocalhost package | ready | Human: accept / bounded_repair / reject |
| G5 bounded repair | 実欠陥だけを直し全編やり直しを避ける | affected timestamp/dimension | conditional | Agent: new identity、限定再検証 |
| G6 Factory Contract v2 | candidate→actual audio→timeline→reviewを再利用可能にする | G4収束 | proposed | Supervisor: schemaと停止条件を抽出 |
| G7 second episode | 一回限りの成功かを判定 | G6最小contract | proposed | Agent: 別episodeでrepeat |
| G8 third episode/trend | repair率とquality driftを観測 | G7 pass | proposed | Supervisor: 3本比較 |
| G9 rights | 技術成果と利用可否を接続 | exact accepted artifact、owner/platform/territory | closed | Rights owner: receipt |
| G10 production subtitle/font | diagnostic字幕をdelivery designへ上げる | G4 accept、font/license | closed | Designer: device/safe-area receipt |
| G11 production render | delivery codec/audio/device QCを閉じる | G9/G10 | closed | Production owner |
| G12 title/thumb/metadata | creative promiseをexact videoへ固定 | final video lock | closed | Editorial owner |
| G13 private delivery | 公開前のauth/idempotency/rollbackを証明 | G9–G12、credentials approval | closed | Account owner |
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

- **Advance**: G4 exact human review。
- **Audit**: low-confidence cueとtitle/rough promiseの確認点を短いdecision packetにする。
- **Explore**: G6 Factory Contract v2を候補schema、alignment、telop、thumbnail、停止条件へ分解する。
- **Verify**: protected SHA、tracked episode 0、Git clean、HTTP 200/206を維持する。

長期依存とowner境界は`docs/SUPERVISOR_STATUS_REPORT.md`を正本とする。
