# 監修AI向け現状報告 — OUT-10 third-source Short human review ready

更新日: 2026-07-19

対象: ClipPipeGen / `codex/out-10-third-source-short-portfolio-expansion-v0`

状態: `OUT10_THIRD_DISTINCT_EXTERNAL_SOURCE_SHORT_REVIEW_READY_WITH_3_SOURCE_SCORECARD`

## 結論

前回の`NO_ELIGIBLE_LOCAL_THIRD_SOURCE_DECISION_READY`に対して与えられたDecision Aを消費し、
一つのbounded external acquisitionを完了した。探索対象は公式hololive channelの公開YouTube動画に
限定し、metadata 5件、詳細preflight 3件、media download 1件、候補1本の上限を守った。

選んだrecordingは `TlnviOwLRmk`。OUT-08 `7J5aS_pcBj4`とOUT-09 `D4i4fjs9PWc`の
accepted authorityとは異なる。冒頭 `0.000–20.304s`と公式日本語caption 15 eventを固定し、
1回のrenderで1080x1920 / 20.333333秒の候補、manifest、frame QA、browser-safe review page、
3-source scorecardを生成した。補正renderは使っていない。

技術検証は通ったが、一本のShortとしての内容・テンポ・字幕可読性・composition・終端は人間未確認。
したがって現在地はinternal human review readyであり、accepted、production-ready、rights-cleared、
public-readyではない。

## Authorityと取得境界

| 対象 | 固定した証拠 | 現在の効力 | 明示的な限界 |
|---|---|---|---|
| official source | `https://www.youtube.com/watch?v=TlnviOwLRmk`、channel ID `UCJFZiqLMntJufDCHc6bQixg` | 第三recording identityと公開状態をanonymous metadataで確認 | rights approvalや二次利用許可の法的判断ではない |
| source video | SHA `8cbb98eeaa62f539fc0a72c7e587bc961f47cb254a1aaabdb11bba7001c4a3a4`、1920x1080、116.517732秒 | local render inputをbyte単位で固定 | ignored local mediaでcross-machine portableではない |
| source audio | SHA `159b95ffbe2cfe7c39923fa14fe4637e432683a58a0a22fcf141b8afe81f56c7` | downloaded videoから既存local-media-audio経路で導出 | 別のnetwork media downloadではない |
| official caption | JA JSON3 SHA `fa9fe66e8a9b5302a66faa7ea256d3e5b500bd0eb5047e9d451d6ee00bc34d21` | candidate 15 cueのtext/timing authority | human transcript acceptanceやproduction subtitle designではない |
| acquisition receipt | `docs/output_layer/out10_external_source_acquisition_receipt.json` | 5/3/1の探索上限、選択理由、hash、tool warningをtracked化 | media byte自体は含まない |

login、cookies、OAuth、DRM、geo/age/anti-bot回避、mirror/reupload、third-party download serviceは
一切使っていない。source acquisitionとcandidate builderを分離し、builderはURL fetchを行わない。

## Bounded selection

| 順位 | video ID | preflight | 採否と理由 |
|---:|---|---|---|
| 1 | `TlnviOwLRmk` | public/not-live、official JA caption、max 1440p、video/audio | 採択。冒頭診察micro-sceneが20.304秒で自然に閉じ、全景保持で9:16化可能 |
| 2 | `23qdzlX4m3Y` | public/not-live、official JA caption、video/audio | 非採択。酩酊premiseがあり、このbounded sliceではeditorial sensitivityが相対的に高い |
| 3 | `BP7H7bASFek` | public/not-live、official JA caption、video/audio | 非採択。multi-location survival場面で短い自然終端とcomposition負荷が高い |

残りmetadata 2件は上限どおり詳細preflightへ進めなかった。popularity最大化や無制限探索ではなく、
最初のeligibleで編集上の危険が低い候補を選んだ。

## Candidateの設計

source inspectionでは、左右に意味のある複数キャラクターとnative name labelが存在した。
center cropは端の人物を失い、source由来blurは文字をcanvasへ複製する。このsourceには
OUT-09のcaption-band crop / blur policyをコピーせず、全1920x1080 frameをneutral matte
`0x0D1624`上へfitした。

| 設計点 | 選択 | workflowへの効果 | 残る判断 |
|---|---|---|---|
| foreground | full-source 16:9 fit、cropなし | 全キャラクターとname labelを保持 | matte余白を含む見栄えはhuman review対象 |
| background | neutral solid matte、source-derived=false | blurによる文字/輪郭の重複を防止 | 共通defaultには昇格しない |
| dialogue caption | official JA event 15 cueをforeground外下部へburn-in | native labelと追加字幕を分離 | 可読性と切替テンポはhuman review対象 |
| endpoint | source 20.304s、次scene transition前 | 台詞が閉じた位置で停止 | Shortとしての終わり感はhuman review対象 |

このpolicyを既存shared rendererへparameterとして追加し、default routeとOUT-09挙動は維持した。
OUT-10 builderはdistinct source identity、acquisition receipt、ledger、official caption、plan hash、
closed gateをfail-closedで検証する。

## 成果物とexact identity

package:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | exact evidence | 用途 |
|---|---|---|
| `candidate_01.mp4` | SHA `9c930f82a2447bbdbae8db477d30d46dd5ad3a7710109dd0cba7117686a4bb2f`、11,138,772 bytes | human review対象 |
| ASS / SRT | 15 cue、SHA `3f66101b...fa05` / `e755bfcc...a06d` | subtitle authorityの可視化と外部readback |
| frame QA | SHA `1b606ed7...fa08`、10 sample | 全景・字幕・終端を静止画確認 |
| navigation frame | SHA `387033fd...3219` | review導線のみ。thumbnailではない |
| plan snapshot | SHA `ad2beb3d...2deb8` | source/hash/range/policyをrender前入力へ固定 |
| readback | SHA `a1c69b31...992b` | media/audio/signal/composition/review boundary |
| manifest | 13 payload、self SHA `c34f39934ab670e5d272bc43bc854936d567e999d940af0a935294bfd8d7abf2` | packageのself-integrity |
| 3-source scorecard | JSON SHA `9f985a0a...f6a7` + HTML | OUT-08/09/10を並べ、欠測値をunknownで保持 |

起動コマンド:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out10_hololive_secret_clinic_20260719\review\out10_third_source_short_portfolio\open_preview.ps1 -Serve -Port 8073
```

clean URLは `http://127.0.0.1:8073/index.html`。serverはreview時だけ前景で維持する。検証後は
停止済みで、port 8073 listener 0を確認した。

## 検証結果

| 検証面 | 実測結果 | 判定境界 |
|---|---|---|
| render budget | execution 1、corrective 0、build 35.604秒 | 契約上限内 |
| media | H.264 High/AAC、1080x1920、30fps、yuv420p、20.333333秒、full decode/faststart pass | 技術的再生性のみ |
| loudness | input -18.50 LUFS/-0.32 dBTP、output -13.93 LUFS/-1.48 dBTP | production mix acceptanceではない |
| signal | blackdetect 0、silencedetect 0 | 長い黒/無音の機械検出なし |
| caption | ASS/SRT/readback 15 cue一致 | 意味/可読性の人間確認は未了 |
| frame | 10/10 extracted、全景と終端を目視 | motion/tempo acceptanceではない |
| manifest | payload 13とself-integrity pass | ignored packageの同一性を固定 |
| HTTP | page 200、Range 206、Content-Range `bytes 0-1023/11138772` | localhost transport proof |
| browser desktop | 1280px、1 video、paused/muted/time 0、readyState 4、overflow false | autoplayなし |
| browser mobile | 375x812、doc width 360、video 329x585、overflow false | physical device proofではない |
| browser QA route | muted playbackが約1.01秒進みpause、media errorなし | clean human URLにはQA queryを残さない |
| console | warning/error 0 | browser runtimeの観測 |
| tests | OUT-10/OUT-09/neutral-matte route pass | 既知OUT-06 CP932 wrap failure 1件は本変更外 |

## 3-source scorecardの読み方

OUT-08/09/10を同じJSON/HTMLに並べたが、過去packageに存在しない測定値は推測せずunknownとした。
このscorecardで証明できるのは、三つのdistinct recordingに対して異なるsource conditionを
記録し、candidate identityとcomposition decisionを比較できることまでである。

証明していないもの:

- 三sourceに共通するproduction-grade自動crop/blur policy
- production subtitle design / mix / image quality
- thumbnail systemの再現性
- rights clearanceやpublic release readiness
- cross-machine package portability

## 人間判断

質問は一つに固定する。

> 一本のShortとして内容とテンポが成立しているか。字幕と音声、字幕の可読性、crop・blur・matteによる重要内容や元字幕の扱い、最後の終わり方に明確な違和感があれば教えてください。

回答はexact MP4 SHA `9c930f82...bb2f`に対するaccept / bounded repair / rejectとして記録する。
現時点は`human_review_pending=true`、`acceptance_granted=false`。

## 今後を最も先まで進める条件付き目標

| 入口 | 解くbottleneck | 必要条件 | 到達可能になる次状態 | 停止条件 |
|---|---|---|---|---|
| Advance | 第三sourceのcreative acceptance不在 | exact candidateへの人間回答 | OUT-10 accepted internal closure、3-source portfolioの確定 | 違和感が一つでも具体化されたらacceptしない |
| Repair | 字幕/音声/composition/endpointの局所欠陥 | defect、保持範囲、再render許可を限定 | 新SHAのcorrective candidateと差分review | source変更、権利判断、広い再編集が必要なら再承認 |
| Audit | scorecardの比較可能性とunknownの整理 | OUT-10 reviewと分離した分析 | shared input validationとsource-specific policyの境界を固定 | 欠測値を推測で埋めない |
| Explore | thumbnail directionの単発proxy依存 | accepted real Shortが3〜5本 | 複数実例によるthumbnail方向比較 | 本数不足の間はOUT-07をcanonical/default化しない |

最遠の安全目標は、(1) exact OUT-10 candidateのhuman gateを閉じ、(2) accepted 3-source evidenceから
共通化できるpreflight/manifest/readbackと人間に残すcomposition判断を分離し、(3) 実Short 3〜5本が
揃った時点でthumbnail探索を再開すること。その先のproduction/public releaseはrightsとowner判断を
別gateで取得した後にのみ計画する。

## 閉じたgate

- rights approval
- production render/subtitle design/image quality acceptance
- thumbnail acceptance
- public/publishing/upload/OAuth/visibility/made-for-kids
- cross-machine media portability
- main merge / canonical promotion

drift監査では、個別sourceに対するneutral matteを一般ruleへ昇格せず、docsだけで完了扱いせず実装・
render・browser evidenceまで接続した。単発artifactの次consumerはhuman review、scorecardの次consumerは
OUT-10受理後のportfolio auditと明確である。
