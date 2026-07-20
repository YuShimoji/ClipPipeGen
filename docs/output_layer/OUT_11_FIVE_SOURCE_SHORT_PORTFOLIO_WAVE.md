# OUT-11 Five-Source Short Portfolio Wave 01

更新日: 2026-07-20

状態: `OUT11_FIVE_SOURCE_SHORT_PORTFOLIO_COMBINED_REVIEW_READY`

artifact: `clip-out11-five-source-short-portfolio-wave-v0-001`

## 目的と到達点

OUT-08/09/10に続く第4・第5の公式公開real sourceを追加し、異なる5 recordingsに対する
source-adaptive Short生成の実績を、winnerやproduction標準を捏造せず一つのscorecardへ揃えた。
OUT-08/09はaccepted context only、OUT-10/04/05だけを人間が見る三動画レビュー面とした。

## Source acquisition

| 段階 | 上限 / 実績 | 結果 |
|---|---:|---|
| metadata exploration | 10 / 10 | 公式channel候補を比較 |
| detailed preflight | 6 / 6 | duration、caption authority、画面構成を観測 |
| media download | 2 / 2 | SOURCE-04/05だけ取得 |
| fallback | 0 / 0 | 不要 |

login/cookies/OAuth/DRM/geo/age/bot bypass、第三者downloader、他repo accessは使っていない。

## 第4ソース

- URL: `https://www.youtube.com/watch?v=PQ54uUV41-k`
- title: `【アニメ】あっははインドネシア〜！`
- channel: `hololive ホロライブ - VTuber Group` / `UCJFZiqLMntJufDCHc6bQixg`
- source video: SHA `f3aa118fb0e903988a9e45abdb31460eff6ecc099ced3d77710b504e0e809d63`
- official direct JA JSON3: SHA `52266947d3ed9a16d5f3e1645709348cede7eecfea7825f544c9f411a2cba91e`
- selected: `0.000–18.500s`、7 cue、caption-clear tail 1.733s
- endpoint candidates: 13.277 reject、16.847 reject、18.500 selected
- composition: full 16:9 fit on neutral matte、crop/blurなし
- final MP4: SHA `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524`
- render: total 2 / corrective 1。初回はfinal loudness QA帯を外れ、shared pass-through判定を
  QA帯内側へ合わせた後に `-14.29 LUFS / -1.49 dBTP` でpass。

最初の47.698–60.950s案はofficial cue overlapのためrender前に破棄し、candidate budget内で
自己完結するcold openへ切り替えた。これは実render失敗に数えない。

## 第5ソース

- URL: `https://www.youtube.com/watch?v=gUwJBRUIWow`
- title: `Dramatic XViltration`
- channel: `hololive Indonesia` / `UCfrWoRGlawPQDQxxeIDRP0Q`
- source video: SHA `8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf`
- official direct ID karaoke JSON3: SHA `919e23b9fc84acec88c4cef677b631d52696a2f7f014a4df45de1c8a1ea3a4a1`
- selected: `202.586–217.650s`、3 semantic lyric lines、native baked lyrics only
- endpoint candidates: 217.180 reject、217.650 selected
- composition: full 16:9 fit on neutral matte、baked lyricを保持、duplicate overlayなし
- final MP4: SHA `370850c5222b70d944f7ba879849f33a2b448edae355e4e41dc35977bf22b578`
- render: 1 / corrective 0、`-13.93 LUFS / -1.88 dBTP`

## Five-source scorecard

scorecardは各sourceについてresolution、language、caption authority、cue統計、composition、
endpoint evidence、render/corrective count、exact MP4 SHA、source-specific debt、再利用可能な
validation、人間に残す判断、rights/production statusを記録する。

OUT-08/09は`accepted_internal`、OUT-10/04/05は`human_review_pending`。winner、
production readiness、universal crop/caption/speaker-color policyはすべてfalseである。

## Combined review

package:
`episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\open_preview.ps1 -Serve
```

clean URL: `http://127.0.0.1:8074/index.html`

一画面・一列・質問一件。三本とも初期paused/muted/currentTime 0、volume ceiling 25%、
autoplayなし。一つを再生すると他をpauseする。機械証拠と5-source scorecardは初期folded。

## Validation

| 検証 | 結果 | 限界 |
|---|---|---|
| source package binding | readback/manifest self/hash/size一致 | same-machine ignored source |
| combined copy | 三MP4すべてsourceとbyte一致 | portabilityではない |
| media | 三本full decode/faststart/signal pass | production encode承認ではない |
| HTTP | page 200、三本Range 206 | localhost transport |
| browser desktop | no overflow、initial safe、exclusive playback pass | physical-device proofではない |
| browser mobile 390 | no overflow、三media ready/error null | responsive browser proof |
| console | warning/error 0 | 観測時点 |
| final 3 seconds | contact sheet/waveformで欠落なし | 意味的自然さはhuman gate |
| package manifest | 14 payload / self integrity pass | ignored package |

## Decision packet

質問:

> OUT-10は最後のセリフまで自然に完結したか。第4・第5候補はそれぞれ一本のShortとして内容・テンポ・字幕・音声・構図・終端が成立しているか。候補ごとに明確な違和感があれば自由に教えてください。

明確な違和感があれば候補名と時点を自由記述する。中間レビュー、二択winner、字幕style選択は
要求しない。

## 次に進める条件

| 入口 | 解く摩擦 | 必要条件 | 次に可能になること |
|---|---|---|---|
| Advance | 三候補のacceptance不在 | exact三SHAへの人間回答 | 候補別accept/repair/rejectの記録 |
| Repair | source-specific違和感 | 時点と現象が特定された回答 | 該当sourceだけのbounded repair判断 |
| Audit | 5 source間の字幕差分debt | 3本が受理され、production subtitle gateが別途開く | 推測なしの字幕differentiation比較 |
| Integrate | main未統合 | OUT-10/11のclosure順序を監修者が承認 | OUT-10を先、OUT-11を後のfast-forward計画 |

## Not Done

human acceptance、winner、rights、production render/subtitle/image quality、thumbnail、
public/publishing/upload/OAuth/visibility/made-for-kids、cross-machine media portability、main merge。
