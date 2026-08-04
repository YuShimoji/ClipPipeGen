# Wiki添削 Long-form Family v1

## 現在の結論

2026-08-05時点で002と003はどちらもcandidate-specific caption/topic/chapter/commentary inputを持つ
`static-reviewable` benchmarkである。003はretained evidenceだけからnetwork request 0で生成した。
両者のexact source bytesは未供給で、media validationとProduct Gateは未達。cookies / OAuth /
anonymous acquisition retryを行わない。15 family / 27 slotの現在の横断入口は
[`../benchmarks/index.html`](../benchmarks/index.html)。002の完全動画条件と権利境界は下記の
まま保持し、完成済みとは扱わない。

`ED-13`は、さくらみこ公式チャンネルの公開`/streams`面を正本surfaceとして、
タイトルが`非公式wiki`または`みこスバ調査隊`に一致する配信を「Wiki添削」familyへ
含める。2026-08-04の再実行では69ページ、2,033 unique streamsをpagination終端まで列挙し、
3本をinventoryした。48 playlistsも終端まで確認したが専用playlistは観測されなかった。

このcomplete claimは「現在公開され、上記の公式stream面とtitle ruleで観測できるもの」に限る。
private、deleted、unlisted、将来の配信が存在しないとは主張しない。補助検索3 queryは発見漏れの
兆候を見るcorroborationであり、網羅性の根拠には使わない。

## Inventory

| video ID | 公開日時 | 長さ | availability / caption | 題名 |
|---|---:|---:|---|---|
| [`1AcId5Yja10`](https://www.youtube.com/watch?v=1AcId5Yja10) | 2025-02-11 23:43:24 +09:00 | 5,558s | `OK` / Japanese auto caption fetched | 我らみこスバ非公式wiki添削隊 |
| [`82iRbxjvbww`](https://www.youtube.com/watch?v=82iRbxjvbww) | 2025-05-04 22:55:55 +09:00 | 6,418s | `OK` / Japanese auto caption fetched | みこスバ調査隊・ゲスト宝鐘マリン |
| [`Ocqg-RpQURY`](https://www.youtube.com/watch?v=Ocqg-RpQURY) | 2026-03-25 21:07:46 +09:00 | 3,522s | `OK` / Japanese auto caption fetched | だぶちーず・非公式wiki調査 |

Authoritative channelは[`Miko Ch. さくらみこ`](https://www.youtube.com/@SakuraMiko/streams)、
channel IDは`UC-hM6YJuNYVAmUWxeIr9FeA`。collectorはpageごとのcontinuation token hash、
raw/unique/duplicate count、pagination exhaustion、canonical inventory SHA、取得時刻をreceiptに残す。

再実行:

```powershell
node src/integrations/asset_fetch/wiki_tensaku_corpus.mjs `
  --output-dir episodes/wiki_tensaku_family_20260804/corpus `
  --max-pages 120 `
  --download-first-source
```

期待値はstreams 69 pages / 2,033 unique / duplicate 0 / pagination exhausted、
playlists 2 pages / 48 unique / dedicated match 0、corpus 3 / available 3。
ネットワークや公開面が変化した場合は、過去値に合わせず新receiptとdiffを出す。

## 最初の完全視聴可能slice

| 項目 | 固定値 |
|---|---|
| artifact ID | `clip-wiki-tensaku-longform-v1-001` |
| source | `youtube:1AcId5Yja10`; public provider combined A/V; source SHA `a994228674d0a6756f8747cf6a07b2cc4c4601fdbf98d5ca0bea3ee2f32060e7` |
| timeline | 全5,557.812245sを12の時系列slotに分け、各slotのcaption-denseな25sを選択; 12 chapters / 300.000s |
| final video | H.264/AAC 640x360; 19,194,868 bytes; SHA `904693b764aa020bcf1834942d93ab30374bf5bdf8d456c265ddfa03e316a36c` |
| captions | source-caption 123 cuesをsidecar SRT/VTTへremap |
| commentary | 12 creator-authored eventsを`editorial_context.json`に分離; source captionとmergeしない |
| validation | 13/13 pass; full decode pass; mapping 1.0; -15.89 LUFS / -3.98 dBTP; black/silence 0 |
| manifest | 17 payload rows; self-integrity `36473a084fb8486eeecdb1c67729d61e167f1ca19fecc015b81ffe3d89740d97` |
| rights | `readback_unresolved`; local/internal diagnostic only; production/public/monetized/uploadは未承認 |

同一マシンでの入口:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-longform-v1-001\review\open_preview.ps1
```

headless/別browserでserverだけ起動する場合:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-longform-v1-001\review\serve_preview.ps1
```

URLは`http://127.0.0.1:8078/review/index.html`。launcherはrepoのローカルPythonを
`uv --offline`で起動し、動画Range requestを受ける。2026-08-04にpage 200、MP4 Range 206、
1,024 bytesを実行確認し、検証processは停止した。

## 第三sourceのnetwork-free static packet

`clip-wiki-tensaku-longform-v1-003`は`youtube:Ocqg-RpQURY`のretained caption payload、
corpus inventory、family topic index、retained watch receiptだけから生成する。実装revisionは
`e7539e03b680d8a79ba7e4c389a69b45130ea0d0`。caption SHA
`a383ad8a545fe9a24da142dace96fe19f05bf834a03e1e52616a5332db3c3992`、979 timed events、
12 topic windows、44 correction anchors、12 chapters、12 creator commentary eventsを持つ。
evidence modeは`retained_caption_inventory_topic_and_watch_snapshot_no_network`、network requestは0。

source bytes、MP4、closed media manifest、full decode、13/13 media QA、localhost playbackは存在しない。
従ってstateは`candidate_specific_static_inputs_ready_no_network`、Product Gateは`NOT_MET`、
external stateは`WAITING_EXACT_SOURCE_BYTES`。static input contractのpassを完成動画の証拠へ拡張しない。

## Provenanceと索引境界

`topic_index.json`はcaption keyword windowからtopic、事件、訂正、前後、関係性を検索可能にする。
これは章候補の索引であり、因果や発話者の意図を確定しない。`source_caption`はprovider caption、
`creator_authored_commentary`は編集上の見出し・注記で、identifierも表示trackも分離する。
公開・production判断には再引用確認、文脈確認、権利判断、人間の編集判断が別途必要。

## CONTINUEする次slice

1. `youtube:82iRbxjvbww`または`youtube:Ocqg-RpQURY`のexact source bytesが明示的に供給された時だけ、
   該当full source rangeをhash固定して既存12章inputから300s / 12 chapters / 13 checksを通す。
2. 3本のvalidated sliceが揃った後、topic/事件/訂正の重複と前後関係を人間が確認し、
   family-level chapter planへsource-range provenanceをbindする。

次sliceの合格条件は、source acquisition SHA receipt、caption receipt、12章すべてのsource mapping、
source-caption/commentary分離、closed manifest、H.264/AAC、full decode、13/13 media QA、localhost
page 200 / MP4 Range 206。権利やproduction/public承認は合格条件へ混ぜず、引き続き閉じる。

S1 `clip-s1-two-source-common-context-probe-v1-001`のS4 human reviewは別laneとして
`pending`のまま駐車し、今回のartifact identity・判断・acceptanceを継承しない。
