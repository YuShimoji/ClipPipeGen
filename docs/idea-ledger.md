---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-25
---

# Idea Ledger - ClipPipeGen

OUT-10/11のShort portfolioはaccepted internal・winnerなしで閉じ、OUT-12の実長尺automationは
operational、OUT-13のcaption-evidence editorial routeはcandidate 005までremote code completeかつ
source-host receiptが成立している。2026-07-25のcurrent root再照合ではcandidate 004 / 005 packageがあり、
candidate 005のinputs / plan / MP4 / digestもcontractと一致した。tracked codeとexact local review targetの
双方が開発可能で、ユーザーはexact candidate 005を内部の全編editorial / visual scopeでacceptした。
accepted revision`18641fe`はmainへfast-forward統合され、M4/M5も完了した。
現在のbottleneckはM6 rights readinessのscopeと判断ownerである。以下は別々の
bottleneckを解く候補であり、proposalやmachine passをhuman、rights、production、public acceptanceへ
自動昇格させない。

| 段階 | 目的 / workflowへの効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| G0: OUT-10/11 closure保持 | accepted Shortを再修復せず比較authorityとして再利用 | exact SHAとreceipt不変 | 完了 | Agent: lineage維持 |
| G1: OUT-12 one-command real video | source→Timeline IR→MP4→validation→review→resumeを一縦糸にする | 取得済みreal source、FFmpeg/ffprobe | 完了。SHA `5d391ffd...a584`; このcheckoutにもlocal evidenceあり | Agent: regression時だけ修復 |
| G2: OUT-13 editorial route | explicit planとcaption evidenceを非連続cut・字幕・reviewable MP4へ運ぶ | source/caption/transcript/rights/plan | remote code complete。candidate 005 MP4 SHA `a76babda...bbb5`とexact local packageを再照合 | Agent: code contract維持 |
| G3: artifact identity recovery | humanがOUT-13 reviewable bytesへ探索なしで到達できるようにする | exact package、plan、hash、single launcher | current hostで完了。25 files / 87,123,995 bytes、digest`ed45fd4c...040` | Agent: same-machine availabilityとGit portabilityを分離 |
| G4: internal editorial acceptance | composition、subtitle presentation、picture/audioを一本で判断 | G3、exact SHA、single review entry | 完了。receiptは`out13_human_acceptance_receipt.json` | Agent:同じmedia/context/dimensionsを再reviewへ戻さない |
| G5: main integration | accepted branchをmainへ安全に接続し、clone可能な開発基線にする | branch全差分preflight、明示統合承認 | 完了。`18641fe`をfast-forward統合しM5 pass | Agent: main baseline維持 |
| G5R: bounded editorial repair | 将来の実変更で影響する判断だけを再確認する | changed/causally affected dimensionとtimestampが明示 | conditional | Agent:影響範囲だけを新identityで修復・再検証 |
| G6: rights/material-use clearance | 技術成功と利用許可を接続する | source/range、権利者/ガイドラインsnapshot、判断owner | `rights=pending` | Rights owner: allow/deny/restriction receipt |
| G7: production subtitle design | 字幕、font/license、safe area、話者表現をproduction判断へ上げる | G4、明示design gate、visual owner | closed | Human designer: exact visual receipt |
| G8: production render acceptance | internal H.264/AACをdelivery仕様へ上げる | G7、delivery/device/color/audio QC仕様 | closed | Supervisor/User: profileとacceptanceを承認 |
| G9: production candidate convergence | G6〜G8の独立receiptを一episode identityへ束ねる | 各gateの個別結果、episode pack contract | proposed | Supervisor: receipt集約として承認 |
| G10: thumbnail + metadata | video確定後の手戻りを減らし非公開delivery準備へ接続 | 複数accepted output、thumbnail再開判断 | thumbnailはpark、metadata未着手 | Human/Agent:別sliceで比較とdraft |
| G11: private/unlisted delivery | public化せずOAuth/idempotency/rollbackを証明 | G6〜G10、credentials明示承認 | 未実装・要承認 | Human owner: credential/visibility gate |
| G12: explicit public release | 制作・権利・公開判断を監査可能に閉じる | private delivery、全owner receipt、rollback | future gate | Human owner:公開直前の明示判断 |
| G13: multi-episode operations | queue/retry/retention/quality trendで継続運用する | G2〜G12のcontract安定、複数episode evidence | long-range proposed | Agent:失敗隔離のthin orchestrationから提案 |

## 次の取っ掛かり

- **Advance**: M6 rights readiness packetのsource/range、snapshot、判断ownerを整理する。
- **Verify**: main baselineのaccepted feature ancestry、full/focused gate、remote parityを維持する。
- **Audit**: rights/source-rangeの判断packetを作り、技術受領と利用許可を分離して閉じる。
- **Explore**: production subtitle designかproduction render profileの一方を、明示gateとしてthin slice化する。
- **Repair**: 将来mediaが変わる場合だけ、影響dimension/timestampを限定しnew identityへ進む。

OUT-12 second-source repeatability debtは消えていない。OUT-13は別sourceを使うが別CLI・別目的であり、
OUT-12 long-form routeの3分以上second-source repeatability passとしては数えない。OUT-13の
M4/M5を閉じた現在は、M6 rights readinessと残るproduct gateを並べて再優先順位付けする。

依存順と各段階の最小証拠は`docs/SUPERVISOR_STATUS_REPORT.md`のportable境界・未完了gate・先へ進む順序を参照する。
