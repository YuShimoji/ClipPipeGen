# OUT-14 Push Micro-Arc Real Stream v1

OUT-14 は、出力を「何本の source を使ったか」ではなく、視聴者へ届ける一話の構造で
分類する portfolio reset の最初の実装である。ここでの三分類はdelivery contractであり、
codec・解像度・縦横比を示すvideo profileではない。実装済み contract は
`PUSH_MICROARC` だけで、`CATALOG_TOPIC_FEATURE` と `EVENT_STACK_RECAP` は比較対象として
正本へ登録するが、このスライスでは生成しない。

## 正本 profile

| profile | delivery intent | 必須構造 | v1 状態 |
|---|---|---|---|
| `PUSH_MICROARC` | 一つの出来事・話題を、発端から余韻まで自然な短編として届ける | hook / necessary context / development / payoff or resolution / completing aftermath。通常 5–15 分、自然な境界を守る場合のみ 4–18 分 | OUT-14 で実装・実 artifact 生成済み |
| `EVENT_STACK_RECAP` | 一つのイベント期間を、時間・因果・結果の積み上げとして再構成する | event boundary、ordered beats、state change、result、aftermath。通常 9–30 分 | 未実装。均等サンプリングや arbitrary thirds を recap と呼ばない |
| `CATALOG_TOPIC_FEATURE` | 複数の独立話題を整理し、章立てで比較・俯瞰させる | topic identity、章ごとの premise、章間の editorial relation、catalog closure。通常 15–45 分 | 未実装。`PUSH_MICROARC` の N-source 版として扱わない |

push / catalog を含むdelivery laneは、source count、collaboration、talent scope、language、
content classと独立した軸である。
OUT-14 実 run は `push / free_talk / solo / single_talent / ja`。同じ
`PUSH_MICROARC` は将来 collaboration や gameplay にも適用できるが、source 固有の権利・第三者 IP・
字幕 authority を別 gate で判断する。

## 実装契約

`build-push-microarc-stream` は、取得済み source MP4、公開完了配信の provider info、
source video/audio receipt、material ledger、rights snapshot、provider caption JSON3 と
匿名 caption receipt、明示 editorial plan を hash で照合する。plan は正確な source complement
となる omission ledger、5 つの semantic role、premise 固有の境界理由を持つ。

v1 は一つの連続 source range を一つの media cut として保持する。semantic role は意味の読取位置であり、
不要な jump cut や画面ラベルを生成する指示ではない。`まず見る`、`ここでは`、`展開`、`結論`のような
汎用ラベルを映像へ足さない。source が premise を直接説明する場合は creator context を 0 件にできるが、
省略理由と source-caption / creator-context namespace 分離 readback を必須にする。

provider 自動字幕は選定・timing evidence であり、公式著者字幕、逐語 transcript、話者同定とは扱わない。
成果物は SRT/ASS、caption readback、semantic evidence linkage を分離して保持する。metadata draft は
description の 1 行目を exact source URL、2 行目を exact source title とし、非公式編集と
非 endorsement を明記する。

active design-direction quarantine は
`two_source_forced_alternation_common_context_v1`、
`unrelated_context_official_anime_interleave_v1`、
`shorts_attention_reset_as_longform_default_v1`。このartifactはどれも使用せず、
rejected two-source probeを修復・流用しない。

## 実 artifact

| 項目 | 値 |
|---|---|
| artifact | `clip-out14-push-microarc-stream-v1-001` |
| source | `youtube:rltNvZ_FY8Q` / `【#生スバル】おはすば！：FREE TALK【ホロライブ/大空スバル】` / public completed stream |
| source identity | SHA `5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240`、4848.047891s、取得解像度 640x360 |
| selected episode | source 786.36–1487.52s、timeline 701.16s、final 701.166667s、utilization 0.144627 |
| premise | 一週間の不在理由から帰省と葬儀の事情を語り、地元・家族の具体話を重ね、帰れて良かったと結ぶ近況報告 |
| structure | 1 continuous media cut、5 ordered semantic roles、2 intentional omissions、178 caption cues、creator context 0 |
| final media | H.264 High / AAC / yuv420p / 1920x1080 / 30fps / 157,691,184 bytes / SHA `1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f` |
| resolution provenance | 640x360 progressive source を Lanczos で 1920x1080 へ拡大。native 1080p の主張はしない |
| validation | full decode、faststart、timestamp monotonicity、A/V sync、-15.0 LUFS、-1.19 dBTP、black/silence 0、caption containment、mapping coverage 1.0 |
| manifest | 29 payload rows + excluded `run_manifest.json`; payload digest `ac8c625320a95df39dfdddc1f67fba3edfcf793ea322886979d0144e9dfd4d03`; self-integrity `f0da343f9d2108fb2ca7b66b0896f497776890efd63a1956a241d1d6117ab403` |
| local review | `episodes/out14_push_microarc_real_stream_20260726/artifacts/clip-out14-push-microarc-stream-v1-001/review/index.html`; server 実行中は `http://127.0.0.1:8078/review/index.html` |
| state | `OUT14_PUSH_MICROARC_REAL_STREAM_READY_FOR_HUMAN_REVIEW` |

最初の render は review helper の暗黙の複数-cut前提により、単一 cut の boundary sample が空になって
fail-closed した。helper を単一選定区間の endpoint evidence へ限定修正し、再実行で成功した。
成功 package の同一入力 `--resume` は 2.822 秒で manifest と閉集合を再検証し、render を行わなかった。

## 人間が判断する範囲

機械 green は構築・identity・decode・timing・mapping・package integrity の証拠である。
次の三点は human review が必要である。

1. 786.36 秒の開始が会話として自然で、1487.52 秒の「帰れて良かった」までで一話が閉じるか。
2. 葬儀を含む個人的内容を切り抜きの premise として扱う編集判断が適切か。
3. provider 自動字幕 178 cue の言語校正。代表 evidence では短時間 cue の「猿み」のような不自然な分割が見える。

`accept` は内部 editorial/visual review identity にだけ bind する。`bounded_repair` は affected timestamp、
caption、layout だけを新 revision として開き直す。`reject` はこの exact artifact の内部候補役を閉じる。
いずれも rights approval、production acceptance、YPP eligibility、thumbnail、Shorts derivative、
upload、publication、visibility change を含まない。

## 条件付きロードマップ

| 段階 | 目的 | 開始条件 | 完了の証拠 |
|---|---|---|---|
| O14-H1 | exact MP4 の全編 human editorial/visual/language review | 現 package を localhost で開けること | SHA と review context に bind した `accept / bounded_repair / reject` receipt |
| O14-H2 | 必要な字幕・boundary だけを修復 | H1 が bounded repair | 変更箇所、理由、新 SHA、affected dimensions の再 review |
| O14-P1 | portfolio 比較面を作る | PUSH の human receipt があること | 三 profile の比較 rubric。未実装 profile を生成済みと表現しない |
| O15 | `EVENT_STACK_RECAP` の最小 vertical slice | event boundary と ordered beats の一次証拠 | state change と aftermath を保持する一成果物 |
| O16 | `CATALOG_TOPIC_FEATURE` の最小 vertical slice | 独立話題を複数含む適格 source と明示 plan | chapter identity と relation が追跡可能な一成果物 |
| O17 | delivery-contract router / batch orchestration | 三 contract の各 human-reviewed specimen | delivery intent を source count から独立して選べる contract test |
| O18 | production/readiness hardening | profile 比較後に採用方向を owner が選択 | fresh-clone reproducibility、dependency/security audit、operational runbook |
| O19 | rights / production / distribution decision | exact release candidate、owner、territory、platform、素材権利が確定 | 独立した approval receipts。技術 green を承認へ代用しない |
| O20 | authorized release and feedback loop | O19 の明示承認と必要 credentials | upload/publication receipt、rollback、post-release metric plan |

O14-H1 が reject の場合は O14-H2 を飛ばし、失敗理由を profile rubric へ反映して O15 または
別の `PUSH_MICROARC` source へ進む。権利・production・public gate が閉じたままでも、O15–O18 の
local internal specimen と reproducibility 改善は進められる。
