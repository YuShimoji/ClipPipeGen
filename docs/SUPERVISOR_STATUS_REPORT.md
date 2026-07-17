# OUT-08 accepted-internal closure report — 2026-07-17

## これは何か

修復後の exact candidate 01 / 02 に対する受領済みユーザー回答
「両方問題ありません」を正本へ記録し、OUT-08を閉じた監修receiptである。環境再構築、
再視聴、media再生成、private package輸送は行っていない。

## 今の状態

| 判断対象 | 正本状態 | 根拠 |
|---|---|---|
| batch | `accepted_all_internal` | exact二本への一括回答をcandidate別identityへ結び付けた |
| candidate 01 | `accepted_internal` | `28.266667s`、17 subtitles、SHA-256 `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` |
| candidate 02 | `accepted_internal` | `53.466667s`、54 subtitles、SHA-256 `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` |
| winner | none | 二本とも受入れ、順位付け・一本化をしていない |
| review | `human_review_pending=false` / `acceptance_granted=true` | 一本の編集単位、テンポ、開始・境界・終端、字幕可読性、音声・映像連続性を受入対象にした |
| rejected range | `cut_009=reject` | candidate 02 max source end `135.219`、reject interval `135.219–144.000`、overlap none |

`sub_067` / `sub_068` はこのexact render内では受入済み。全動画共通の字幕規則や
production subtitle design acceptanceには昇格させない。

## Constraints / Risks

rightsは`pending`。production render、production subtitle design、thumbnail、
public/publishing、upload/OAuth/visibility/made-for-kidsはfalseまたはunopenedのまま。
Planner007にexact packageが無く再視聴できなくても、記録済みacceptanceは失効しない。

正本lineageはsource branch tip
`2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2`。recovery branch tip
`d1f44d17e9747419f307706cad802aefdd012efd`は
`PARKED_OPTIONAL_NONCANONICAL_INFRA_PROOF`としてremoteに保持し、closure branchや
mainへmerge / cherry-pickしていない。

## 次に進める入口

OUT-08は追加reviewや輸送を要求せず閉じる。次の製品軸はdata-only successor
`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY`。異なるsourceまたはepisodeから、既存
Shorts pipelineを大規模に書き換えず、最低1本の12〜60秒・9:16・reviewable
candidateを生成できることを将来のacceptance signalとする。OUT-09はこのclosureでは
実装していない。

残るquality debtは、`sub_067` / `sub_068`を別sourceでも許容できる字幕規則と誤認
しないこと。revisit triggerはOUT-09以降で同種のwrap問題が再発した場合、または
production subtitle design gateを明示的に開く場合である。
