# Wiki添削 Long-form Family v1

## 現在の結論

2026-08-05時点で002と003はどちらもcandidate-specific caption/topic/chapter/commentary inputを持つ
`static-reviewable` benchmarkである。003はretained evidenceだけからnetwork request 0で生成した。
両者のexact source bytesは未供給で、media validationとProduct Gateは未達。cookies / OAuth /
anonymous acquisition retryを行わない。一方、exact retained source bytesを持つ001から、既存成果を
上書きせず訂正anchor主導のTurn 1と、既存rangeを完全除外するTurn 2/3/4を完全視聴可能にした。
15 family / 32 slotの現在の横断入口は
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

## 訂正anchor主導のFamily Turn 1

`clip-wiki-tensaku-family-turn-v1-001`は、同じ`youtube:1AcId5Yja10`を別artifact identityで
編集比較できるsuccessorである。collectorの`--offline-existing-evidence
--reuse-retained-source-media --selection-profile correction-led`は、retained watch/captionに加え、
acquisition receiptのsource identity、SHA、byte size、duration、`cookies_used=false`、
`oauth_used=false`を照合し、network request 0で入力を閉じる。offline rights timestampはcorpusの
観測時刻へ固定し、同一入力rerunのfingerprint driftを防ぐ。

全5,557.858秒を12の時系列slotへ分け、各slot内でcorrection/verification anchor、topic多様性、
caption evidenceの順に25秒を選ぶ。12/12章に訂正anchorを含み、選択anchorは23件、topic軸は
`correction_and_verification`、`before_after_change`、`relationships_and_collaborations`、
`quoted_phrases_and_wording`の4種。これはkeyword indexに基づく候補選択で、意味・意図・正誤の
人間判断を代行しない。source caption 106 cuesとcreator-authored commentary 12 eventsは分離する。

final MP4はH.264/AAC 640x360 / 300.000s / 21,800,858 bytes、SHA
`1f965e537d5a767d8cfe5c456ed0481ea88a119743f207ada9764bbc0ebe3284`。13/13、full decode、
faststart、A/V sync、black/silence 0、mapping 1.0をpassした。manifestは17 payload rows、
self-integrity SHA`84e9c788c0840a35148755ba3ac6975eade7c80f4f6fd4c85f8bbd9ad1ada971`。
deterministic resumeはanalysis/caption remap/render/media validationをskipし、MP4 hashとmtimeを保持。
localhostはpage 200、MP4 Range 206 / 1,024 bytesをfresh確認後停止した。

同一マシンでの入口:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-family-turn-v1-001\review\open_preview.ps1
```

machine validationはhuman editorial acceptanceではない。次のproduct actionはexact MP4 SHAへ
`accept / bounded repair / reject`をbindすること。いずれの判断もrights、production subtitle/design、
thumbnail、public/monetized use、publishing、uploadを開かない。

Turn 1のtechnical / production-transition acceptanceは固定済みで、artifact自体は変更しない。
human editorial reviewだけがopenであり、rightsやpublic useへの継承はない。

## 未使用range主導のFamily Turn 2

`clip-wiki-tensaku-family-turn-v2-001`は、baselineとTurn 1のexact `edit_pack.json`を入力として
24 selected rangesを除外し、同じ`youtube:1AcId5Yja10`の未使用caption-backed rangeだけを選ぶ。
binding SHAはbaseline `d2af54b14724774c27dae5322e263b206dd4bbd7b38d93daecd29dd74f5bbf86`、
Turn 1 `61c3a9e90fa9fd6abf9a2d37c93e901398441a79cdeb2b3f3230edc0d219f406`。
選択rangeとのoverlapは0秒で、12/12章にcorrection anchor、合計20 anchorsを持つ。
network requestsは0、source SHAは`a994228674d0a6756f8747cf6a07b2cc4c4601fdbf98d5ca0bea3ee2f32060e7`、
caption SHAは`f58c248f23b29845a94ae01b789f122c8759687125375a2650cc7a8074107e4f`のまま。

final MP4はH.264/AAC 640x360 / 300.000s / 19,951,636 bytes、SHA
`2736f6ec5b4a779a70c978d7815639802dee2d294220fdbb592edb9d75fe2dca`。13/13、独立full decode、
mapping 1.0、black/silence event 0をpassし、resumeは4 cache hits / `render_executed=false`で
hashとmtimeを保持した。unique source-time unionは575秒から875秒へ増え、5,558秒inventoryに対し
10.35%から15.74%となった。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-family-turn-v2-001\review\open_preview.ps1
```

この増分はsource-timeの網羅性であり、意味的網羅性や人間の編集評価を自動的に示さない。

## 三世代range除外のFamily Turn 3

`clip-wiki-tensaku-family-turn-v3-001`はbaseline、Turn 1、technical-accepted Turn 2の
3 edit packs / 36 rangesを除外する。binding SHAは順に
`d2af54b14724774c27dae5322e263b206dd4bbd7b38d93daecd29dd74f5bbf86`、
`61c3a9e90fa9fd6abf9a2d37c93e901398441a79cdeb2b3f3230edc0d219f406`、
`b50e1c01becf415ed2a1247f20c24a398abdb744709f5f4b7a58f4fd18f64906`。
12章はすべて未使用rangeで、overlap 0秒。11/12章にcorrection anchor、合計12 anchorsを持つ。
slot 6の唯一のcorrection event `2595.04–2601.64s`はTurn 1/2のrangeと交差するため、重複せず
含めることはできない。選択器は非correction caption-backed rangeへ降格し、既使用rangeへは戻らない。

final MP4はH.264/AAC 640x360 / 300.000s / 20,605,376 bytes、SHA
`5abfd8e940bd8a2709e79aced38ab2e0e56b7f052f3d205512e082d2a8f8733b`。13/13、独立full decode、
mapping 1.0、black/silence 0、93 caption cuesをpass。resumeは4 cache hits / renderなしで
hashとmtimeを保持した。unique source-time unionは875→1,175秒（+300秒）、coverageは
15.74%→21.14%。HTTPはfresh検証しておらず、page/Range成功を今回の証拠として主張しない。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-family-turn-v3-001\review\open_preview.ps1
```

Turn 2までのhuman editorial/terminal/rights/publication gateは待機状態のまま継承せず、Turn 3も
同じopen gateへparkする。Wiki 002/003とS1のgateは変更しない。

## 四世代range除外のFamily Turn 4

`clip-wiki-tensaku-family-turn-v4-001`はbaselineとTurn 1〜3の4 edit packs / 48 rangesを
exact SHAで除外した。追加bindingとなるTurn 3 edit-pack SHAは
`8928d7378fb27759d73dea5c9ce72c22a37c7fd2e33db61b0ca375a56da292bb`。
12章はすべて未使用rangeでoverlap 0秒、network requestも0。9/12章に各1件、合計9件の
correction anchorを持つ。

caption-backed fallbackは第1・6・12章の3件。各slotには未使用caption候補が残るが、既使用rangeを
除外した後にcorrection anchorを含む25秒windowは3 slotとも0件だった。Turn 3の1件から増加したため、
意味的な編集適合はSupervisor watch itemとして渡し、12/12 correctionを捏造しない。

final MP4はH.264/AAC 640x360 / 300.000s / 18,884,819 bytes、SHA
`5fea3d14e476871f239d1ab42283fedd83546daf98e8c5a27f625506ba69ca40`。13/13、独立full A/V decode、
mapping 1.0、black/silence 0、86 caption cuesをpass。manifest self-integrity SHAは
`61badb088ef6adbe59e624a1290ae88adecd44cc5b9c320b2eef2be6863c5d83`。resumeは4 cache hits、
`render_executed=false`でMP4 SHAとmtimeを保持した。unique source-timeは1,175→1,475秒、
coverageは21.14%→26.54%。HTTPはfresh検証しておらず成功を主張しない。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-family-turn-v4-001\review\open_preview.ps1
```

このmachine evidenceはhuman editorial/terminal、rights、full production、public/monetized use、
publishing、upload acceptanceを開かない。Turn 3 artifact、Drive identity、Feedback provenance、
Wiki 002/003 exact-source gate、S1 gateは変更しない。

## 五世代range除外のscarcity-aware Family Turn 5

`clip-wiki-tensaku-family-turn-v5-001`はbaselineとTurn 1〜4のedit packsを実ファイルから再集計し、
5 packs / 60 selected rangesをexact SHAでbindして除外した。追加bindingとなるTurn 4 edit-pack SHAは
`cc07d91f385e48f6325ad4030552ac4be19f5bb1da0c237fbfceb452c8b65020`。Turn 5の12章はすべて
prior rangeとoverlap 0秒で、retained source/caption以外を使わずnetwork request 0で生成した。

実測構成は`correction-prioritized-mixed`。第2・3・4・5・7・8・9・10章の8章に各1 correction anchorを
持つ。fallbackは4章あり、第1章は未代表topic `before_after_change`を追加するため、第6・11・12章は
各slotの未使用correction-bearing 25秒候補が0件になった後に時系列の意味連続性を維持するため選択した。
各章のcaption候補数、除外数、未使用correction/fallback候補数は`editorial_context.json`へ個別記録した。
12/12 correction-ledとは主張しない。

final MP4はH.264/AAC 640x360 / 300.000s / 19,964,780 bytes、SHA
`e192fcd6746d396c0c92b5952c274cf5afd07f47c0f5d3a17deecd33b658012c`。13/13、built-inと独立full A/V
decode、mapping 1.0、black/silence 0、96 caption cuesをpass。manifest self-integrity SHAは
`819e4c049c21f186ef003101642ecd3f51192d41f4567869af4324e327bc7586`。resumeは4 cache hits、
`render_executed=false`でMP4 SHA・size・mtimeを保持した。unique source-timeは1,475→1,775秒、
coverageは26.54%→31.94%（+300秒 / +5.40pt）。HTTPはfresh検証しておらず成功を主張しない。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\wiki_tensaku_family_20260804\artifacts\clip-wiki-tensaku-family-turn-v5-001\review\open_preview.ps1
```

Turn 4はexact MP4 SHAへboundした`continue / bounded repair none / correction-prioritized mixed`判定として
不変。Turn 5のhuman editorial/terminal、rights、production、publication、recipient restoreはopenのまま。
Wiki 002/003 exact-source gateとS1 gateも変更しない。

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

1. Family Turn 5のexact MP4 SHA、8 correction章、4 fallback章とchapter別scarcity evidenceを
   Supervisor editorial reviewへ渡す。
2. `youtube:82iRbxjvbww`または`youtube:Ocqg-RpQURY`のexact source bytesが明示的に供給された時だけ、
   該当full source rangeをhash固定して既存12章inputから300s / 12 chapters / 13 checksを通す。
3. 3本のvalidated source sliceが揃った後、topic/事件/訂正の重複と前後関係を人間が確認し、
   family-level chapter planへsource-range provenanceをbindする。

次sliceの合格条件は、source acquisition SHA receipt、caption receipt、12章すべてのsource mapping、
source-caption/commentary分離、closed manifest、H.264/AAC、full decode、13/13 media QA、localhost
page 200 / MP4 Range 206。権利やproduction/public承認は合格条件へ混ぜず、引き続き閉じる。

S1 `clip-s1-two-source-common-context-probe-v1-001`のS4 human reviewは別laneとして
`pending`のまま駐車し、今回のartifact identity・判断・acceptanceを継承しない。
