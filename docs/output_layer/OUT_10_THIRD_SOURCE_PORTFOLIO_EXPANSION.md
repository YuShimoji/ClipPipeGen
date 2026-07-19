# OUT-10 Third-Source Short Portfolio Expansion v0

更新日: 2026-07-19

artifact: `clip-out10-third-source-short-portfolio-expansion-v0-001`

state: `OUT10_THIRD_DISTINCT_EXTERNAL_SOURCE_SHORT_REVIEW_READY_WITH_3_SOURCE_SCORECARD`

## 到達点

前段のlocal inventory stopに対するDecision A（bounded external acquisition）を消費し、
OUT-08 `7J5aS_pcBj4`、OUT-09 `D4i4fjs9PWc`とは異なる第三のreal recording
`TlnviOwLRmk`から、human review用Short候補を1本生成した。取得対象は公式hololive channelの
公開動画に限定し、metadata 5件、詳細preflight 3件、media download 1件、候補1本の上限を
すべて守った。

builderは外部取得を行わない。取得済みsource video/audio、公式caption、material ledger、
rights snapshot、edit pack、declarative planのidentity/hash/区間を照合してから既存vertical
rendererを再利用する。これによりacquisition判断とrender判断を分離している。

## Source選定

| 順位 | source | preflight | 判断 |
|---:|---|---|---|
| 1 | `TlnviOwLRmk` | public、not live、1920x1080以上、video/audio、official JA caption | 採択。冒頭診察場面が20.304秒で閉じ、全景保持で9:16化できる |
| 2 | `23qdzlX4m3Y` | public、video/audio、official JA caption | 酩酊premiseを含み、この小sliceではeditorial sensitivityが高いため非採択 |
| 3 | `BP7H7bASFek` | public、video/audio、official JA caption | multi-location survival sceneで、短区間の自然な閉じと全景保持負荷が高いため非採択 |

login、cookies、OAuth、DRM、geo/age/anti-bot回避、mirror/reupload、第三者download serviceは
使っていない。yt-dlpはanonymous metadata/preflightと公式media/caption取得にだけ用い、
source audioは取得済みvideoからlocal-media-audio経路で導出した。

| authority | exact identity |
|---|---|
| source video | SHA `8cbb98eeaa62f539fc0a72c7e587bc961f47cb254a1aaabdb11bba7001c4a3a4`、1920x1080、116.517732秒、AV1/AAC |
| source audio | SHA `159b95ffbe2cfe7c39923fa14fe4637e432683a58a0a22fcf141b8afe81f56c7`、local derivation |
| official JA JSON3 | SHA `fa9fe66e8a9b5302a66faa7ea256d3e5b500bd0eb5047e9d451d6ee00bc34d21` |
| tracked acquisition receipt | `docs/output_layer/out10_external_source_acquisition_receipt.json` |

## 候補設計とcomposition

候補はsource `0.000–20.304s`、公式caption冒頭15 eventをそのままtiming/text authorityにした。
診察室への歓迎から、患者を送り出してゴルフへ移る台詞までで一つのmicro-sceneが閉じ、
次のscene transitionより前で終了する。

9点のsource frameを先に確認した結果、左右に意味のある複数キャラクターとsource-native name
labelが存在した。center cropは端の人物を落とし、source-derived blurはname labelの字形を
canvasへ複製する。そのため今回は全1920x1080 frameをneutral matte `0x0D1624`上にfitし、
次を明示的に禁止した。

- crop
- source-derived background / blur
- native caption pixel suppression
- frosted subtitle surface
- full-source blur fallback

対話字幕はforeground外の下部canvasへASSでburn-inした。これはOUT-10 sourceに対する
probe結果であり、OUT-09のcaption-band cropも今回のneutral matteも共有defaultではない。

## Review package

local path:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | identity / role |
|---|---|
| `candidate_01.mp4` | SHA `9c930f82a2447bbdbae8db477d30d46dd5ad3a7710109dd0cba7117686a4bb2f`、H.264/AAC、1080x1920、20.333333秒 |
| `candidate_01.ass` / `.srt` | 公式JA由来15 cue。ASS SHA `3f66101b...fa05`、SRT SHA `e755bfcc...a06d` |
| `candidate_01_frame_qa.jpg` | 10 frame sample、SHA `1b606ed7...fa08` |
| `candidate_01_navigation.jpg` | 導線用代表frame、SHA `387033fd...3219`。thumbnail acceptanceではない |
| `candidate_plan.json` | fixed input snapshot、SHA `ad2beb3d...2deb8` |
| `candidate_readback.json` | media/audio/signal/frame/browser boundary、SHA `a1c69b31...992b` |
| `candidate_manifest.json` | 13 payload file、self SHA `c34f39934ab670e5d272bc43bc854936d567e999d940af0a935294bfd8d7abf2` |
| `source_portfolio_scorecard.json` | OUT-08/09/10 3-source row、SHA `9f985a0a...f6a7` |
| `source_portfolio_comparison.html` | 人間向けscorecard比較。前任sourceの欠測値はunknownのまま |
| `index.html` | video-first、autoplayなし、安全なlocalhost review page |

起動:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out10_hololive_secret_clinic_20260719\review\out10_third_source_short_portfolio\open_preview.ps1 -Serve -Port 8073
```

前景serverを明示起動する場合:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out10_hololive_secret_clinic_20260719\review\out10_third_source_short_portfolio\serve_preview.ps1 -Port 8073
```

clean URLは `http://127.0.0.1:8073/index.html`。server windowはreview中だけ開き、終了は
`Ctrl+C`。検証後のlistenerは停止済みで、未知のport ownerをkillする実装はない。

## 検証結果

| 検証 | 結果 |
|---|---|
| render budget | actual render 1、corrective pass 0 |
| media | full decode/faststart passed、H.264 High/AAC、30fps、yuv420p、video/audio各1 stream |
| audio | input -18.50 LUFS/-0.32 dBTP、output -13.93 LUFS/-1.48 dBTP |
| signal | blackdetect 0、silencedetect 0 |
| caption | ASS/SRT/readbackすべて15 cue、official JSON3 authority |
| frame QA | 10/10 extracted。全景、name label、burn-in subtitle、endpointを目視確認 |
| manifest | 13 payload hashとself-integrity passed |
| HTTP | page 200、MP4 Range 206、Content-Range `bytes 0-1023/11138772` |
| browser | desktop/mobile overflowなし、clean URLはpaused/muted/time 0、QA routeだけ再生後pause、console warning/error 0 |
| renderer regression | OUT-10/OUT-09/new neutral-matte tests passed。既知のOUT-06 CP932 wrap failure 1件は本変更外 |

## Human review gate

質問は一つだけである。

> 一本のShortとして内容とテンポが成立しているか。字幕と音声、字幕の可読性、crop・blur・matteによる重要内容や元字幕の扱い、最後の終わり方に明確な違和感があれば教えてください。

accept / bounded repair / rejectはexact MP4 SHA
`9c930f82a2447bbdbae8db477d30d46dd5ad3a7710109dd0cba7117686a4bb2f`へ結ぶ。
現時点では`human_review_pending=true`、`acceptance_granted=false`。

## 閉じたままの境界

- rights approval
- production render / subtitle design / image quality acceptance
- thumbnail acceptance（navigation frameはthumbnailではない）
- public/publishing/upload/OAuth/visibility/made-for-kids
- cross-machine media portability
- OUT-10のcanonical/main統合

OUT-08/09 accepted internal authorityは変更していない。3-source scorecardはportfolio comparisonの
入口であり、production repeatabilityや普遍的なcomposition ruleの証明ではない。
