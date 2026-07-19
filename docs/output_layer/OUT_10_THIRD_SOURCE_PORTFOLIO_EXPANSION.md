# OUT-10 Third-Source Short Portfolio Expansion v0

更新日: 2026-07-20

artifact: `clip-out10-third-source-short-portfolio-expansion-v0-001`

state: `OUT10_ENDPOINT_BOUNDED_REPAIR_REVIEW_READY`

## Outcome

第三source `TlnviOwLRmk`、開始点`0.000s`、主題、全景neutral matte、白字幕style、
音量方針、artifact IDを維持し、人間観測でMUST-FIXになった終端だけを修復した。

旧candidateはsource `0.000–20.304s`、media 20.333333s、15 cue、MP4 SHA
`9c930f82a2447bbdbae8db477d30d46dd5ad3a7710109dd0cba7117686a4bb2f`。
内容・テンポ・字幕/音声同期・字幕可読性・neutral matte構図・safe playbackは合格したが、
最後のtelopと映像動作が完了する前に切れた。acceptanceは与えず、
`superseded_predecessor_endpoint_too_early_active_telop_motion`としてlineageへ残す。

新candidateはsource endを`27.711s`へ7.407秒延長し、公式JA captionを30 cue追加した。
冒頭15 cueの本文・時間・白styleは変更していない。full render 1回、corrective 0回。

## Endpoint probe

probe windowは旧終端`20.304s`から最大12秒先の`32.304s`まで。source EOF、freeze、
fade、black frame、end card、合成telopは使わず、実映像と実音声だけを比較した。

| end | caption / audio | frame / motion | 判断 |
|---:|---|---|---|
| 20.304s | golf line終了直後 | impact/telop/actionがこれから始まる | reject |
| 22.840s | scream系列終了 | 大きな膝telop説明が続く | reject |
| 24.308s | 膝line終了 | BAUBAU reactionが同時に開始 | reject |
| 25.242s | BAUBAU終了 | foreground人物の進入と「急患発生」開始 | reject |
| 26.310s | 「急患発生」終了 | operation lineとthumb-up actionが継続 | reject |
| 27.711s | 「オペを執り行いますよ！！」と音声が完了 | thumb-up pose成立。次shotは約27.733s | selected |

`27.711s`は、caption・発話・telop・動作がすべて完了し、次の検査dialogueへ踏み込む前の
最初の自然な区切りである。次shotまで約0.022秒しかなく、静止画保持や人工transitionは不要。

## Caption change

- total: 45 official Japanese JSON3 event cue
- unchanged predecessor cues: 15
- added cues: 30（event index 15–44 / segment `seg_000016–seg_000045`）
- added range: `20.304–27.711s`
- last cue: `オペを執り行いますよ！！` / `26.310–27.711s`
- ASS SHA: `8388568204876e01cbf51632e9867bcab5013dfe8f350835adac089e70277a03`
- SRT SHA: `27d6bf5b13d0d11de28b15d5d9df37bc373b80a86ee6682cd408588c2cb7b892`

20.304–22.840sの短い反復scream eventも、公式JSON3のevent boundaryを改変せず連続cueとして保持。
speakerを推測せず、全cueの既存白styleを維持した。

## Exact package

local path:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | exact identity / role |
|---|---|
| `candidate_01.mp4` | SHA `3651a14f408d9c5935399007d750a42d349d6c672dd0a80071be6cbcb53d9884`、15,508,592 bytes |
| media | H.264/AAC、1080x1920、30fps、yuv420p、27.733333s |
| `candidate_01_frame_qa.jpg` | SHA `49991a274cf3a71d3cef3fe7a8d330a6577841980b9e6005ab013744f4e9aef1`、11 samples |
| `candidate_01_navigation.jpg` | SHA `ebe773d706a9c26a8b7630415e77b82f988116af3fffdc7f2349da6b869974f1`、navigation only |
| `candidate_plan.json` | SHA `3219292698ba47bb695537d0b1af86f02520c91f23271cf407e19e9a20ff55cb` |
| `candidate_readback.json` | SHA `834584c05fa1d88b8d1a750b1d0ffdd1abc0fd8d73ba0ba424ce23f00c4f0933` |
| `candidate_manifest.json` | 13 payload、self SHA `59441786bce520c3c17d4a8ebd000985b14654bddd33dd69d0512754ded4465a` |
| `source_portfolio_scorecard.json` | SHA `b4008ad570506f72c63bd0f1546f451eb1c4d298a63c45574644146b422d168a` |
| `index.html` | SHA `a86e338b93127f69ef4bb3aed04cbde1e6cd3321122910d6dfbee96727ee4f57` |

scorecardはOUT-10のmedia identity、duration、subtitle count、endpoint status、predecessor SHAだけを
更新した。OUT-08/09は不変、winnerは選ばず、production repeatabilityも宣言しない。

## Validation

| 面 | 結果 |
|---|---|
| render budget | full render 1、corrective 0、build 60.279s |
| media | full FFmpeg decode / faststart passed |
| audio | output -13.87 LUFS / -1.31 dBTP |
| final 3s audio | RMS -13.75 dB、peak -1.50 dB、NaN/Inf 0、silence event 0 |
| signal | blackdetect 0、silencedetect 0 |
| caption | ASS 45 / SRT 45 / readback 45、last end 27.711s |
| final frame QA | 24.711〜27.611sを0.5s刻み＋0.1s前で7 sample、caption/action/pose completion確認 |
| manifest | self-integrity true、13/13 payload hash一致 |
| HTTP | page 200、MP4 Range 206、`bytes 0-1023/15508592` |
| clean browser | paused/muted/currentTime 0、readyState 4、autoplay attrなし、media errorなし |
| responsive | desktop 1280 / mobile 375x812、horizontal overflowなし |
| QA route | muted playback約1.07s後pause、clean URLへ戻してtime 0 |
| console | warning/error 0 |

## Review access

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out10_hololive_secret_clinic_20260719\review\out10_third_source_short_portfolio\open_preview.ps1 -Serve -Port 8073
```

clean URL: `http://127.0.0.1:8073/index.html`

exact artifactを返すforeground serverを確認済み。未知port ownerはkillせず、同一artifact/SHA/Rangeの
場合だけreuseする。

## Human gate

> 最後のテロップや動きが途中で切れず、一本のShortとして自然に終わるようになったか。既に合格していた字幕・音声・構図に明確な回帰があれば併せて教えてください。

回答は新MP4 SHA `3651a14f...9884`へbindする。
`human_review_pending=true`、`acceptance_granted=false`。

## portfolio_subtitle_differentiation_debt

全字幕が白で話者識別が弱い点はdeferred debt。今回、話者別色分け、speaker badge、字幕位置分け、
speaker identity推定は行っていない。現白styleを一般標準として承認しない。

再検討条件:

- 3〜5本のaccepted real Shortsによるportfolio比較後
- production subtitle-design gateが明示開始された時

## Closed gates / Not Done

- human acceptance
- rights approval
- production render/subtitle design/image quality acceptance
- thumbnail acceptance
- public/publishing/upload/OAuth/visibility/made-for-kids
- cross-machine media portability
- scorecard winner
- main merge / PR / rebase / squash

OUT-08/09 package、OUT-06 wrap debt、shared renderer、source取得、冒頭・中盤は変更していない。
