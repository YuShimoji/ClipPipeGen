# OUT-14 Push Micro-Arc Editorial Reconstruction v2

## 目的

v1の人間editorial rejectionを、字幕だけの美容修正で処理せず、episode選定から再構成した
review candidate。3 stream identity、9 episode candidate、11 competitive observationsを
比較し、v1とdisjointなDiscordプロフィール通知エピソードを選んだ。

artifactは`clip-out14-push-microarc-editorial-v2-001`。
stateは`OUT14_PUSH_MICROARC_EDITORIAL_V2_READY_FOR_HUMAN_REVIEW`。

## v1から継承したものと閉じたもの

v1 final SHA `1db41c4f...d07f`のsource acquisition、mapping、render/decode、A/V、
localhost deliveryはtechnical evidenceとして保存する。人間editorial verdictは`rejected`。
decision正本は`OUT_14_V1_HUMAN_EDITORIAL_DECISION.json`。

active quarantine:
`out14-contiguous-auto-caption-unstructured-v1`

v2はv1 span overlap 0、既知の
`981.199–1008.720` / `1052.080–1075.799`を完全除外。funeral/deathを主要hookにする
C1はscore前hard gateでrejectした。

## selection contract

| 項目 | 値 |
|---|---|
| stream identities | 3 |
| episode candidates | 9 |
| score前hard gates | premise、closed arc、sensitivity、quarantine、chronology、anonymous media、actual-audio feasibility |
| competitive observations | 11 |
| winner | C3 Discordプロフィール変更が全体通知になった朝 |
| score | 93 / 100 |
| v1 overlap | 0秒、excluded fraction 1.0 |
| output profile | 180–420秒 normal contract内 |

selectionとcompetitive dataはartifact内の
`selection_record.json` / `competitive_coverage.json`。

## source contract

| 項目 | 値 |
|---|---|
| source identity | `youtube:rltNvZ_FY8Q` |
| anonymous formats | video 399 + audio 251 |
| acquired window | provider 2268–2910秒 |
| media | 1920x1080/60、AV1/Opus、642.001秒 |
| SHA | `335e9a131fae06b716bd7ac479e914fb849be117b15c4b412c9b4c565fef264e` |
| access | cookies/OAuth/credentialsなし |
| clock origin | measured 2268.03秒、cross-correlation 0.859306、request差+30ms |

local source receipt、ledger、rights snapshotはepisode配下にあり、Gitへtrackしない。

## editorial timeline

| section | provider source seconds | role |
|---|---:|---|
| premise setup | 2276.48–2326.76 | Discord profile premise |
| red-card setup | 2392.92–2457.80 | おかゆが選んだアイコン |
| work context | 2468.88–2521.44 | 仕事返答での見え方 |
| profile escalation | 2556.20–2632.48 | 背景・statusを変更 |
| notification reveal | 2645.20–2737.28 | 全体通知の判明 |
| apology | 2775.40–2806.00 | スタッフ・外部friendへの謝罪 |
| aftermath | 2841.24–2861.00 | 朝5時の恥ずかしさ |
| ending warning | 2886.32–2906.40 | 視聴者への注意 |

chronologyは維持し、cold openやsource order changeは使わない。

## transcript / subtitle contract

viewer-facing字幕の正本はselected actual audioへbindしたfaster-whisper small
word timing。provider JSON3はimmutable discovery provenanceで、viewer authorityはfalse。

単語時刻でcut内の語だけを取り込み、最大16文字へchunkする。Discord等の固有語を
不可分lexical unitへmergeしてから分割し、非発話annotationを除去する。

| gate | 結果 |
|---|---:|
| cues | 142 |
| anchors | 24、各section 3 |
| median signed onset error | 0.0ms |
| absolute p95 | 0.0ms |
| non-speech display count | 0 |
| presentation violations | 0 |

## visible structure、title、thumbnail rough

creator-authored telopはspeechと別provenance。

1. `Discordのプロフィールを変えた朝`
2. `遊びで変え続けた結果`
3. `変更通知が届いていた`
4. `変更は全体通知される`

working title:
`Discordのプロフィールを遊びで変えたら、全スタッフに通知が飛んでいた`

alternatives:

- `おかゆとプロフィールをいじった結果、通知先に戦慄するスバル`
- `「蒙古タンメン スバル」が全スタッフに共有された朝`

thumbnail roughはactual source frameのみ。1280x720と320x180を作り、
`全スタッフに通知`をreview補助として表示する。生成画像、production/publication
thumbnail acceptanceではない。

## final artifact

| 項目 | 値 |
|---|---|
| final video | H.264/AAC yuv420p、1920x1080、406.55秒 |
| byte size | 405,217,162 |
| video SHA | `8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414` |
| manifest SHA | `774351a7fc55839e05e58276280570a27ac1fd0aa7fa78283cdcf79f5d8634a9` |
| package | 30 files / 408,275,872 bytes |
| media validation | 13 / 13 pass |
| audio | -14.93 LUFS、-1.85 dBTP、cut delta 0.82 LU |
| HTTP | review 200、MP4 Range 206 |

review entry:
`episodes/out14_push_microarc_editorial_v2_20260727/artifacts/clip-out14-push-microarc-editorial-v2-001/review/index.html`

open:

```powershell
powershell -NoProfile -File episodes\out14_push_microarc_editorial_v2_20260727\artifacts\clip-out14-push-microarc-editorial-v2-001\review\open_preview.ps1
```

## 人間判断

このexact SHAへ`accept / bounded_repair / reject`を記録する。
scopeは構成、cut自然さ、言語、字幕presentation、telop、title、thumbnail rough。
rights、font/license、production render、YPP、upload、publication、visibilityは含まない。

bounded repairはaffected timestamp/dimensionだけを新identityへ移す。
unmentioned regionをaccept済みと扱わない。

## 次の依存

human verdictが収束したら、candidate card、actual-audio align、timeline、telop、
thumbnail diagnosticをFactory Contract v2へ抽出する。次に別episodeでsecond/third
repeatabilityを確認する。rights、production subtitle、production render、
title/thumbnail acceptance、private delivery、public releaseはそれぞれ独立receiptが必要。
