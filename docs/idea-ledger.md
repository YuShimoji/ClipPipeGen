---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-23
---

# Idea Ledger - ClipPipeGen

OUT-10/11のShort portfolioはaccepted internal・winnerなしで閉じ、OUT-12の実長尺automationは
operational、OUT-13のcaption-evidence editorial routeはremote code completeである。以下は別々の
bottleneckを解く候補であり、proposalやmachine passをhuman、rights、production、public acceptanceへ
自動昇格させない。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: OUT-10/11 closure保持 | accepted Shortを再修復せず比較authorityとして再利用 | exact SHAとreceipt不変 | 完了 | Agent: lineage維持 |
| G1: OUT-12 one-command real video | source→Timeline IR→MP4→validation→review→resumeを一縦糸にする | 取得済みreal source、FFmpeg/ffprobe | 完了。SHA `5d391ffd...a584`; このcheckoutにもlocal evidenceあり | Agent: regression時だけ修復 |
| G2: OUT-13 editorial route | explicit planとcaption evidenceを非連続cut・字幕・reviewable MP4へ運ぶ | source/caption/transcript/rights/plan | remote code complete、606 tests pass。local MP4 SHA `84ed7aa6...791d7e2`一致 | Agent: code contract維持 |
| G3: exact local review access | humanがOUT-13 exact bytesを探索なしで見られるようにする | local plan/package、launcher、hash readback | 完了。25 files、resume 0.281s、page 200 / Range 206 | Agent: local retained artifactとportable contractを分離維持 |
| G4: internal editorial acceptance | composition、subtitle presentation、picture/audioを一本で判断 | G3、exact SHA、single review entry | pending。artifact回収は不要 | Human reviewer: accept / bounded repair / rejectをSHAへbind |
| G5: bounded editorial repair | reviewで特定されたsource-specific欠陥だけを直す | G4がrepair、変更対象と非対象が明示 | conditional | Agent:一回のbounded repairと再検証 |
| G6: rights/material-use clearance | 技術成功と利用許可を接続する | source/range、権利者/ガイドラインsnapshot、判断owner | `rights=pending` | Rights owner: allow/deny/restriction receipt |
| G7: production subtitle design | 字幕、font/license、safe area、話者表現をproduction判断へ上げる | G4、明示design gate、visual owner | closed | Human designer: exact visual receipt |
| G8: production render acceptance | internal H.264/AACをdelivery仕様へ上げる | G7、delivery/device/color/audio QC仕様 | closed | Supervisor/User: profileとacceptanceを承認 |
| G9: production candidate convergence | G6〜G8の独立receiptを一episode identityへ束ねる | 各gateの個別結果、episode pack contract | proposed | Supervisor: receipt集約として承認 |
| G10: thumbnail + metadata | video確定後の手戻りを減らし非公開delivery準備へ接続 | 複数accepted output、thumbnail再開判断 | thumbnailはpark、metadata未着手 | Human/Agent:別sliceで比較とdraft |
| G11: private/unlisted delivery | public化せずOAuth/idempotency/rollbackを証明 | G6〜G10、credentials明示承認 | 未実装・要承認 | Human owner: credential/visibility gate |
| G12: explicit public release | 制作・権利・公開判断を監査可能に閉じる | private delivery、全owner receipt、rollback | future gate | Human owner:公開直前の明示判断 |
| G13: multi-episode operations | queue/retry/retention/quality trendで継続運用する | G2〜G12のcontract安定、複数episode evidence | long-range proposed | Agent:失敗隔離のthin orchestrationから提案 |

## 次の取っ掛かり

- **Review**: このcheckoutのexact OUT-13 packageを一本通してhuman reviewする。現在の最短critical path。
- **Audit**: review結果を待つ間にplan/failure/resume contractを監査し、修復時のstop条件を先に明文化する。
- **Verify**: main統合後、OUT-12 routeをdistinct 3分以上sourceでrepeatし、単一source最適化を検出する。
- **Advance**: OUT-13受理後、rights、production subtitle design、production renderの一gateだけを開く。

OUT-12 second-source repeatability debtは消えていない。OUT-13は別sourceを使うが別CLI・別目的であり、
OUT-12 long-form routeの3分以上second-source repeatability passとしては数えない。現在はOUT-13 human
consumerを先に閉じ、その後のproduct gateと並べて再優先順位付けする。

依存順と各段階の最小証拠は`docs/SUPERVISOR_STATUS_REPORT.md`のM0〜M10 goal ladderを参照する。
