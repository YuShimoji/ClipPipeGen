---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-26
---

# Idea Ledger - ClipPipeGen

ED-12 / S1のtwo-source common-context probeはtracked implementationとsame-machine exact
packageまで到達した。現在はS4 human review pending。以下は違うbottleneckを解く候補であり、
人間判断、rights、production、public acceptanceへ自動昇格しない。

| 段階 | 目的 / 効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0 OUT-13 archive保持 | deny済みexact artifactを再混入させない | Candidate 005 identity不変 | 完了 | Agent: negative boundary維持 |
| G1 S1 identity / strategy | materially distinct successorを明示する | new identity、二source、new thesis | 完了 | Agent: contract維持 |
| G2 evidence-bound plan | cut/commentaryをdirect evidenceへ戻す | media/caption/rights hash | 完了 | Agent: provenance維持 |
| G3 reviewable package | exact MP4とvideo-first pageを作る | FFmpeg、immutable empty output | 完了 | Agent: package hash維持 |
| G4 human common-context review | 二sourceが一つの論として成立するか判断 | exact SHA、全編視聴 | pending | User/Supervisor: accept / bounded repair / reject |
| G5 bounded closure | verdictをidentityへbindする | G4回答 | proposed | Agent: receipt、必要ならnew identity |
| G6 second-pair repeatability | 一例の偶然成功を減らす | G5 accept、別pair | proposed | User:実施価値判断、Agent:thin slice |
| G7 fresh rights inventory | 実際に使う二source/rangeだけ棚卸し | G5 acceptまたは対象確定 | closed | Rights owner: material/range packet |
| G8 production subtitle design | caption/commentary/attributionをdelivery仕様へ上げる | rights条件、design owner | closed | Human designer: exact visual receipt |
| G9 production render | codec/audio/device/QCをdelivery profileへ上げる | G7/G8 | closed | Supervisor/User: profile acceptance |
| G10 episode acceptance pack | lineageと判断receiptを一束にする | G5/G7/G8/G9 | proposed | Agent: no-scope-widening manifest |
| G11 thumbnail / metadata | rights-cleared素材で非公開delivery準備 | G10 | parked | Human/Agent:比較・draft |
| G12 external-state dry-run | upload前にidempotency/rollbackを検証 | G10/G11、no credentials | future | Agent: read-only plan |
| G13 private delivery | public化せず限定導通 | credential/visibility明示承認 | future gate | Human owner |
| G14 public release | 最終公開判断を監査可能にする | 全receipt、release owner | future gate | Human owner |
| G15 operations | queue/retry/retention/quality trend | 複数episode evidence | long-range | Agent: failure isolationから提案 |

## 次の取っ掛かり

- **Advance**: exact S1 MP4をS4の四問だけでreviewし、意味判断のbottleneckを閉じる。
- **Verify**: remote branch parity、package hash、manifest closed setを再確認し、別端末handoffを強くする。
- **Audit**: two sourceの使用rangeとrights unknownをread-only棚卸しし、S4とpermission判断を分離する。
- **Explore**: S4後のsecond-pair候補を比較する。取得・render・generic framework化はまだ行わない。

保留debtは、OUT-12 long-form routeのsecond-source repeatability、S1のsecond-pair
repeatability、caption/commentaryのproduction design、二source各rangeのrights observation。
優先順位はS4 verdict後に再評価する。
