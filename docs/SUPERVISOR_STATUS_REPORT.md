# 監修AI向け現状報告 — OUT-10 endpoint bounded repair review ready

更新日: 2026-07-20

対象: ClipPipeGen / `codex/out-10-third-source-short-portfolio-expansion-v0`

状態: `OUT10_ENDPOINT_BOUNDED_REPAIR_REVIEW_READY`

## 結論

人間観測で合格した内容・テンポ、字幕/音声同期、字幕可読性、neutral matte構図、安全なreview
routeを継承し、早すぎた終端だけを修復した。source、開始点、主題、冒頭・中盤、字幕style、
音量、artifact IDは不変である。

旧MP4 `9c930f82...9884` / source end `20.304s`は、最後のtelopと動作が始まる地点で
切れていたため未受理predecessorとした。旧終端から最大12秒先までをframe/audio/captionで比較し、
`27.711s`を最初の自然な区切りとして選択した。ここではoperation-declaration caption/音声と
thumb-up poseが完了し、約0.022秒後の`27.733s`で次shotへ切り替わる。

新候補はMP4 SHA `3651a14f...9884`、semantic 27.711s、media 27.733333s、45 official JA cue。
full render 1回、corrective 0回。現在はexact new SHAへのhuman review待ちであり、accepted、
production-ready、rights-cleared、public-readyではない。

## 変更前後

| 比較軸 | predecessor | endpoint repair | 効果 |
|---|---|---|---|
| source identity | `TlnviOwLRmk` | 同一 | recording driftなし |
| source start | 0.000s | 0.000s | 冒頭・中盤再編集なし |
| source end | 20.304s | 27.711s | telop/発話/動作を完了 |
| media duration | 20.333333s | 27.733333s | 7.4秒だけ実映像・実音声を延長 |
| subtitles | 15 official JA cue | 45 cue | 既存15不変、必要な30 cueだけ追加 |
| composition | neutral matte/no crop/no blur | 同一 | 合格済み構図を維持 |
| MP4 SHA | `9c930f82...9884` | `3651a14f...9884` | acceptance継承なし、新SHAへ判断をbind |
| status | endpoint too early / unaccepted | human review pending | MUST-FIXの客観検証完了 |

旧SHAのlineage reasonは
`superseded_predecessor_endpoint_too_early_active_telop_motion`。
旧候補にacceptanceは記録していない。

## Endpoint evidence

| probe | caption/audio | visual state | 判断 |
|---:|---|---|---|
| 20.304s | golf line終了 | impact beatとtelop/actionが未完 | reject |
| 22.840s | scream系列終了 | 膝telop説明が続く | reject |
| 24.308s | 膝line終了 | BAUBAU reaction開始 | reject |
| 25.242s | BAUBAU終了 | foreground進入と「急患発生」開始 | reject |
| 26.310s | emergency line終了 | thumb-up motionとoperation line継続 | reject |
| 27.711s | operation line/音声終了 | thumb-up pose完成、次shot 27.733s | selected |

27.711sより先は次の検査dialogueへ入り、27.711sより前はcaptionまたは動作が未完だった。
したがって、別topicへ踏み込みすぎずvisual completionも満たす最初の境界である。
freeze、fade、black frame、end card、logo、新transitionは使っていない。

## Caption authority

追加範囲は`20.304–27.711s`、official JSON3 event index 15–44、
`seg_000016–seg_000045`の30 cue。最後は
`オペを執り行いますよ！！` / `26.310–27.711s`。

短い反復scream eventも公式event timingのまま連続表示し、speaker identityを推測していない。
ASS/SRT/readbackは45 cueで一致し、既存15 cueの本文・時間・白styleに変更はない。

## Exact artifact

package:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | identity |
|---|---|
| candidate MP4 | `3651a14f408d9c5935399007d750a42d349d6c672dd0a80071be6cbcb53d9884` / 15,508,592 bytes |
| ASS / SRT | `83885682...7a03` / `27d6bf5b...b892` |
| frame QA | `49991a27...aef1` / 11 sample |
| plan | `32192926...55cb` |
| readback | `834584c0...0933` |
| manifest | 13 payload / self `59441786...465a` |
| scorecard | `b4008ad5...168a` |

3-source scorecardはOUT-10のmedia identity、duration、caption count、endpoint statusだけ更新した。
OUT-08/09のaccepted factsは変更せず、winner、production readiness、白字幕の一般標準を
宣言していない。

## Validation

| 検証 | 実測 | 限界 |
|---|---|---|
| render | 1 full / 0 corrective / 60.279s | 人間acceptanceではない |
| media | H.264/AAC、1080x1920、30fps、yuv420p、full decode/faststart pass | production encoding acceptanceではない |
| loudness | -13.87 LUFS / -1.31 dBTP | production mix gateではない |
| final 3s audio | RMS -13.75dB、peak -1.50dB、NaN/Inf 0、silence 0 | 聴感の人間確認はreview questionへ残す |
| signal | black/silence event 0 | 機械検出 |
| final frames | 24.711〜27.611sを7 sample | caption/action/pose completion確認 |
| manifest | self true、13/13 payload hash一致 | same-machine ignored package |
| HTTP | page 200、Range 206、0-1023/15508592 | localhost transport |
| desktop | paused/muted/time0、readyState4、overflow false | physical device proofではない |
| mobile | 375x812、video 328.84x584.63、overflow false | responsive browser proof |
| QA | muted playback約1.07s後pause、media error 0 | clean URLはQA queryなし |
| console | warning/error 0 | browser runtime観測 |

## portfolio_subtitle_differentiation_debt

全字幕が白でspeakerを識別しにくい点はdeferred。今回は終端だけがscopeであり、話者別色分け、
speaker badge、字幕位置分け、speaker identity推定を実装していない。
現行白styleを一般標準として承認しない。

再検討条件:

- accepted real Shortsが3〜5本揃いportfolio比較を行う時
- production subtitle-design gateが明示的に開始された時

## 人間判断

review入口:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out10_hololive_secret_clinic_20260719\review\out10_third_source_short_portfolio\open_preview.ps1 -Serve -Port 8073
```

clean URL: `http://127.0.0.1:8073/index.html`

質問は一つだけ:

> 最後のテロップや動きが途中で切れず、一本のShortとして自然に終わるようになったか。既に合格していた字幕・音声・構図に明確な回帰があれば併せて教えてください。

回答は新SHAへbindする。human reviewを飛び越える次実装は起動しない。

## 次に推奨する入口

| 入口 | 解く摩擦 | 必要条件 | 次に可能になること |
|---|---|---|---|
| Advance | endpoint acceptance不在 | exact new SHAへの肯定回答 | OUT-10 accepted internal closure |
| Report regression | 合格済み面の回帰 | 字幕・音声・構図の具体的観測 | 同じSHAへdefectを記録し、再実装前にscope判断 |
| Audit later | 字幕speaker差分のdebt | 3〜5本acceptedまたはproduction subtitle gate | 推測なしのspeaker differentiation比較 |

最遠の安全目標は、まず新SHAのhuman gateを閉じること。その後にのみOUT-10 closureと3-source
portfolio比較を確定し、accepted real Shortsが3〜5本揃った時点で字幕/thumbnail systemの比較へ進む。

## Not Done / 閉じたgate

- human acceptance
- rights approval
- production render/subtitle design/image quality acceptance
- thumbnail acceptance
- public/publishing/upload/OAuth/visibility/made-for-kids
- cross-machine media portability
- scorecard winner
- main merge / PR

shared renderer、OUT-08/09 package、OUT-06 wrap debt、tracked mediaには触れていない。
