# OUT-11 Five-Source Short Portfolio Wave 01 — repair review

更新日: 2026-07-21

状態: `OUT11_HUMAN_REVIEW_REPAIRS_COMBINED_REVIEW_READY`

artifact: `clip-out11-five-source-short-portfolio-wave-v0-002`

## 目的と今回の判断反映

5 recordingsのsource-specific evidenceを維持しつつ、2026-07-21の人間レビューを旧exact SHAへ
結び付けた。SOURCE-04は問題なしとして同じMP4をaccepted receiptへ移し、再render・remux・
transcode・編集をしていない。OUT-10とSOURCE-05は不合格理由をlineageへ残し、実媒体を先に
観測してから各1回のrenderで修復した。

| slot | 人間判断を結んだ旧SHA | 処理 | 現在状態 |
|---|---|---|---|
| OUT-10 | `a53d0416...134f2` | 導入を保持し終端だけ修復 | 新SHAをhuman review pending |
| SOURCE-04 | `465d732c...16524` | 問題なし。exact bytes不変 | `accepted_internal` receipt、再視聴不要 |
| SOURCE-05 | `370850c5...b578` | 画面切替直後終了を同一source内で修復。歌唱・歌詞推定を撤回 | 新SHAをhuman review pending |

OUT-08/09もaccepted comparison contextのまま。winnerや共通production policyは選ばない。

## 修復後の二候補

| 表示順 | source range | 新exact MP4 | 実内容と終端根拠 |
|---|---|---|---|
| OUT-10 | `youtube:TlnviOwLRmk` / `0.000–34.785s` | `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd` / 19,319,488 bytes | 意識確認・患者反応・「ゴッドハンドやね」まで完了。34.800sの別キャラクター紹介を含めない |
| SOURCE-05 | `youtube:gUwJBRUIWow` / `202.586–260.643s` | `b4a01413202e3e177a11dc42754d38f5a4b7b10cd7c7bec0aa43536d440a4969` / 20,469,323 bytes | カード列、イラスト列、最終カード卓、title/credit holdをsource EOFまで保持。終端audioは自然に減衰 |

SOURCE-05のofficial ID JSON3はtimed-text landmarkとしてのみ保持する。実媒体で歌唱・歌詞を
確認したとは扱わず、speaker count、歌詞意味、native lyricをscorecardやreview copyで主張しない。

## SOURCE-04不変証拠

source package:
`episodes/out11_source04_indonesia_laugh_20260720/review/out11_source04_candidate/`

- review前後のMP4 SHA:
  `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524`
- review前後のbyte size: `8,523,260`
- accepted receiptはreadback/manifestを統合packageへcopyするが、SOURCE-04 MP4はcopyしない。
- 合格範囲は当該候補の一本としての流れと終端だけ。rights、production、字幕一般則は未承認。

## Five-source scorecard

| slot | human status | media role | source-specific debt |
|---|---|---|---|
| OUT-08 | `accepted_internal` | context only | 既受理候補を再開しない |
| OUT-09 | `accepted_internal` | context only | speaker identity未確認・低解像度source |
| OUT-10 | `human_review_pending` | active repair review | 新しい診察場面の自然なclosureを確認 |
| SOURCE-04 | `accepted_internal` | accepted receipt only | exact bytesを保持。字幕差分はproduction gateまで保留 |
| SOURCE-05 | `human_review_pending` | active repair review | speech/singing/lyrics/native text semantics未確認。audio-visual unitを確認 |

scorecardは5 rows、active review mediaは2、accepted receiptは1。winner、production readiness、
universal crop/caption/speaker-color policyはfalseのまま。

## 統合review

package:
`episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/`

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out11_five_source_short_portfolio_20260720\review\out11_five_source_short_portfolio\open_preview.ps1 -Serve
```

clean URL: `http://127.0.0.1:8074/index.html`

SOURCE-04 receiptの後、OUT-10、SOURCE-05の順に二動画を表示する。各節はcandidate名、source範囲、
実内容、確認点、exact SHAを明記する。clean URLは両方paused/muted/currentTime 0、volume ceiling
25%、同時再生なし、自動再生なし。muted QA playbackは明示query `?qa-playback=1`だけで起動する。

質問は一件:

> 修復後OUT-10は新しい診察場面の反応と台詞まで自然に閉じたか。修復後SOURCE-05はカード列から最終タイトルまでの音声・映像・終端が一つの単位として成立したか。二本それぞれに明確な違和感があれば自由に教えてください。

## 機械検証

| 対象 | 結果 | 限界 |
|---|---|---|
| OUT-10 media | H.264/AAC、1080x1920、30fps、decode/faststart、black/silence、50-cue containment pass | 意味的自然さはhuman gate |
| SOURCE-05 media | H.264/AAC、1080x1920、30fps、decode/faststart、`-14.02 LUFS/-1.49 dBTP`、silence 0、black 0.767s < 1.5s threshold | 歌唱・歌詞の知覚確認を主張しない |
| final 6s evidence | 二本の0.5秒刻みcontact sheetとPCM waveformを確認 | 同一マシンignored evidence |
| package binding | source readback/manifest/self-hash、MP4 hash/size、13 payloadを検証 | media portabilityではない |
| scorecard | 5 rows / active media 2 / receipt 1 | winner・production policyなし |

combined files:

- readback SHA `4e6160915d80bdcef58cfa407e6be3e74daf4be002dc14d2a9b02f6fda54b406`
- scorecard SHA `4b388531fb3093fd10449d7722656d2ea8dcae8bf9e4d0783d0b63f61ed0d2c9`
- manifest file SHA `e72de3fe092aafb72aa7dd59208c2c07e715c307ce9aac92ada61ae8e632a390`
- manifest self SHA `58276967cb2328f3a8b9ea8813bb85a4847f84e26e8bd465206c56d3e87da7bd`

## 次に進める条件

| 入口 | 解く摩擦 | 条件 | 次に可能になること |
|---|---|---|---|
| Advance | 修復二本のacceptance不在 | 上記一問へのcandidate別自由記述 | exact新SHAごとのaccept / bounded repair / reject記録 |
| Verify | SOURCE-05の意味単位の不確実性 | audio・visual・EOFの具体的観測 | 歌詞推定なしで候補を閉じるかparkする判断 |
| Audit | 5-source字幕差分debt | 二本受理後かつproduction subtitle gateを別途開始 | speaker推測なしの比較設計 |
| Integrate | main未統合 | OUT-10/11 closure順を監修者が承認 | OUT-10を先、OUT-11を後にするfast-forward計画 |

human acceptance、winner、rights、production render/subtitle/image quality、thumbnail、
public/publishing/upload/OAuth/visibility/made-for-kids、cross-machine media portability、main mergeは未完。
