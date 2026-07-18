# OUT-09 Second-Source Short Repeatability

OUT-09 は、OUT-08 で成立した縦型 Short の生成経路が、別の実 source / episode
でも大規模 rewrite なしに成立するかを検証する narrow slice である。2026-07-18
JST 時点で実装、初回review、ユーザー指摘二点への1回のbounded repair、
media/frame/mobile/browser QAまで完了し、同じlogical candidateを再レビューへ渡せる。

この成果は `review_ready` であり、creative acceptance、production render、
production subtitle design、rights approval、public/publishing acceptance のいずれも
意味しない。OUT-08 の accepted identity は変更せず、OUT-09 は別 artifact として扱う。

## source identity と OUT-08 との差

| 項目 | OUT-08 | OUT-09 |
|---|---|---|
| YouTube provider ID | `7J5aS_pcBj4` | `D4i4fjs9PWc` |
| source / episode | Hololive Bancho JP pilot | Ouro Kronii `【Kroniicle Animation】 Wisdom Teeth Removal Woes` |
| episode directory | `jp_pilot01_hololive_bancho_20260525` | `holoen01_kronii_wisdomteeth_out09_20260718` |
| transcript authority | imported official JP subtitle track | imported YouTube English (Original) auto-caption track、base Vosk EN transcript を保持 |
| candidate source range | OUT-08固有の未使用複数範囲 | continuous `31.160–64.480s` |
| human state | exact二本を `accepted_internal` | bounded repair後の新SHAへ`human_review_pending` |

source URL はrepoで既知の
`https://www.youtube.com/watch?v=D4i4fjs9PWc`。既存の `fetch-source-video` /
`fetch-source-audio` adapterを使い、rights manifestはschema-validのまま
`compliance_check.status=pending`を維持した。

現行yt-dlpはJavaScript runtime未構成のため利用可能formatが制限され、取得videoは
`640x360 / H.264 / AAC / 30fps / 77.786848s`だった。OUT-09 outputは既存vertical
rendererで `1080x1920`へ構成しているが、source解像度そのものが上がったとは主張しない。

## ユーザー指摘とbounded repair

初回候補へのfeedbackは`overall=bounded_repair_required`として記録した。内容選択はreject
でもacceptでもなく、subtitle presentation/timingとendpoint editだけが
`needs_adjustment`である。

| 対象 | 初回 | 修復後 |
|---|---|---|
| subtitle authority | ClipPipeGenの長文ASS burn-in + source-native caption | source-native caption pixelsのみ。追加burn-in 0 |
| ASS/SRT | 7表示eventを動画へburn-in | 9eventをprovenance/navigation/machine-readback sidecarとして保持し、動画へ焼かない |
| endpoint | `58.880s`、native captionの`Man,`と発話の途中 | `64.480s`、最後のcaption `64.360s`・発話`64.362812s`完了後、次scene直前 |
| exact MP4 | `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9` | `3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916` |

source-native captionが判読不能なら別案をrenderせず
`REFRAME_REQUIRED_NATIVE_CAPTION_NOT_LEGIBLE`で止める契約にした。実画像では1080x1920と
216x384相当の双方で判読可能だったため、reframeへ拡張していない。

## transcript と編集 authority

Vosk EN small modelは実STTとして13 segmentを生成したが、固有表現と台詞の誤認識が
多かったため表示字幕の正本にはしなかった。公開動画から取得できた YouTube
English (Original) JSON3を既存`import-subtitle-track`へ通し、source-audio readbackを
保持した `subtitle_track/youtube_subtitles` transcript-compatible artifactを使用した。

| authority | readback |
|---|---|
| base Vosk transcript | real STT、13 segments、比較/provenance用。表示字幕の正本ではない |
| source caption import | 24 segments、24/24 aligned、schema pass、provider `youtube_subtitles` |
| overlap debt | rolling caption由来で21 segmentがtiming overlap。human transcript acceptanceは主張しない |
| edit cuts | target 28sで3候補、context check `3 passed / 0 needs_review` |
| selected authority | `cut_002` + `cut_003` envelope内の `31.160–58.880s` |
| display normalization | `rolling_caption_dedup_subsequence_v1`。各display文のtoken列がlinked source segmentsのsubsequenceであることをrender前に検証 |

candidateは、他の配信者を見る視聴者への嫉妬を否定しつつ「私が恋しかった？」と聞き、
自分はone-of-a-kindだと言い切って次sceneへ移る直前までを、33.320秒で構成した。

## 宣言的 plan と fail-closed guard

ignored `out09_candidate_plan_input.json` がsource identity、material IDs/hashes、6つの
input paths/hashes、allowed/excluded ranges、cut/segment linkage、sidecar字幕、
user feedback、native-caption-only mode、自然終端evidence、一つのreview question、
閉じたgateを宣言する。builderは次をrender前に拒否する。

- provider IDがOUT-08 `7J5aS_pcBj4`と同一
- rights source URL/titleとplan identityが不一致
- 6つのauthority fileのいずれかがhash不一致
- material ledgerが実 acquisition routeでない、またはmedia hash不一致
- real transcript provider / segment linkageが不一致
- context-passed cut envelope外、allowed range外、excluded/unselected rangeとのoverlap
- sidecar字幕がlinked source caption textのtoken subsequenceでない
- 追加burn-inが有効、native caption pixelsを変更、ASS/SRTを表示authorityに戻す
- last caption/last speech完了前、無音区間外、次sceneと異なる固定padding終端
- 12〜60秒外、sidecar字幕が非連続、review questionがexact一件以外、gateが開いている

今回のexcluded authorityは`0.000–31.160s`と`64.480–77.786848s`で、candidateとの
source-time overlapは0。これはOUT-08のcut decisionを流用したものではなく、OUT-09
plan固有のunselected rangeである。

## candidate package

| 項目 | 実測 |
|---|---|
| artifact_id | `clip-out09-second-source-short-repeatability-v0-001` |
| state | `OUT09_SUBTITLE_AUTHORITY_AND_ENDPOINT_REPAIRED_REVIEW_READY` |
| ignored package | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/` |
| source range / semantic duration | `31.160–64.480s` / `33.320s` |
| media duration | `33.333333s` |
| media | H.264 High / AAC / `1080x1920` / 30fps / yuv420p / faststart |
| video size / SHA-256 | `6,637,874 bytes` / `3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916` |
| subtitles | native caption pixelsのみ表示。ASS/SRT 9eventはsidecar-only、追加burn-in 0 |
| manifest self-integrity | `440c73dde6b33e9ba9ce63a512e61f5974e947032a507ac17c560d560a028078` |
| plan input SHA-256 | `e9e68b1a9dcd1b1edc0691a5cb43675235aa54f4d1a37ddf36b96a7d93fc53c1` |
| repair render count | actual corrective render `1`、追加autonomous repair `0` |
| elapsed | builder `31.729s`、外側実測 `32.276s` |

packageにはMP4、ASS/SRT、5点frame QA contact sheet、代表navigation JPG、plan、
readback、manifest、single-video HTML、`open_preview.ps1`、Range対応server scriptが入る。
navigation frameはreview移動補助でありthumbnailではない。

## 入力 hash と provenance

| role | SHA-256 |
|---|---|
| source video material | `61c06f75cf914deb0f5cc358c9a2405e2206166b10724533aff9c478f49fd938` |
| source audio material | `b33b3521e495edf13675b91bbbd6b89642ea28e46cd38555e77862cd6315f81b` |
| rights manifest | `d3921bdc9c057d58d3561d4659f1118178170658475e3e487ae69ed656e844f3` |
| material ledger | `6e8422e145d70ca668487e93be2ac1ada0f679722ca21000626e489505724393` |
| base Vosk transcript | `145e62ab99998ee91adb2607b7229755054df1d0adc4709acd8d85280a2d7c73` |
| English Original JSON3 | `36bdbf38f90ede72aef8590c3ef19f88bee3b122a005c4e230fb92af4f3083e6` |
| imported authoritative transcript | `37d37ad287b89dbb6286849052f88b57f832253b3e3816ef3a74838368a2a728` |
| edit pack | `c27834305df970e576079af6c47cdb9d104f04328d43331764849bba4258d049` |

これらはpackageのmanifest/readbackにも記録され、plan・ledger・実fileの協調置換を
hash mismatchで閉じる。

## media / frame / browser QA

| 検証 | 結果 |
|---|---|
| FFprobe | 1 video + 1 audio、H.264/AAC、1080x1920、30fps、yuv420p |
| full decode | video/audio mapを最後までdecode、exit 0、stderr empty |
| faststart | `moov` before `mdat`、passed |
| loudness | input `-27.77 LUFS / -6.87 dBTP`からnormalize、output `-14.80 LUFS / -1.46 dBTP` |
| blackdetect | `d=0.5:pix_th=0.10`、event 0 |
| silencedetect | `noise=-50dB:d=1.0`、event 0 |
| frame QA | `0.250 / 15.160 / 23.500 / 31.320 / 33.070s` の5点をcontact sheet化 |
| HTTP | `index.html=200`、MP4 `Range: bytes=0-1023`=`206`、1024 bytes |
| browser media | `readyState=4`、native video `1080x1920`、duration `33.333333s`、media error null |
| browser interaction | Space play/pause、ArrowRight seek、resume `1.558→2.454s`へ前進 |
| desktop/mobile | default幅と375px client幅でoverflow false。mobile上のvideo幅341.8pxでnative caption判読可能 |
| layout / console | horizontal overflow false、review question exactly 1、warning/error 0 |

frame contact sheetでは、source-native横長画面を中央へ保ち、上下をblurred extensionで
埋めるOUT-05系reframeを維持した。追加の長文caption、`support`途中wrap、native caption
との二重表示は最終MP4にない。ASS/SRTにはprovenanceとして9eventを残したが、renderに
渡すinternal ASSはDialogue 0件で、package/readback/manifestもburn-in=falseを一致させた。

終端調査ではsource `64.360s`で最後のnative caption、`64.362812s`で最後の発話が終わり、
`64.362812–64.541125s`に短い無音があり、`64.480s`で次scene/captionが始まることを確認。
このscene transitionをend-exclusive boundaryにしたため、固定padding、fade、SFX、freeze、
追加無音なしで、最後の画面beatを保持して次sceneへ入らない。

## review entrypoint と質問

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

URL: `http://127.0.0.1:8072/index.html`

人間へ渡す質問は次の一つだけである。

1. 字幕の切替リズムと終わり方が自然になったか、ほかに明確な違和感があれば教えてください。

回答前は`human_review_pending=true`、`acceptance_granted=false`。回答が得られた場合も、
このexact MP4 hashへ判断を結び、production/public/rights gateを同時に開けない。

## 再生成 command

```powershell
uvx python -m src.cli.main build-second-source-short-repeatability `
  --episode-dir episodes\holoen01_kronii_wisdomteeth_out09_20260718 `
  --output-dir episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability `
  --candidate-plan-input episodes\holoen01_kronii_wisdomteeth_out09_20260718\out09_candidate_plan_input.json `
  --ffmpeg C:\Users\thank\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe `
  --ffprobe C:\Users\thank\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe `
  --format json
```

絶対tool pathは同一マシン実行例であり、manifest/readbackにportable dependencyとして
埋め込まない。`episodes/`はignored、`git ls-files episodes`は0を維持する。

## evidence boundary とH1 successor data

OUT-09が証明したのは、別provider ID・別episode・英語caption authority・低解像度
16:9 sourceでも、宣言的planから1本のreviewable vertical Shortと検証packageを作れる
ことまでである。次は証明していない。

- YouTube auto-caption全文のhuman transcript acceptance
- 640x360 sourceのproduction画質acceptance
- native-caption-only modeの他sourceへの一般化
- 修復後exact MP4のhuman acceptance
- rights/material-use approval、production/public/publishing readiness
- ignored packageの端末間portability
- 二つ目のsource成功だけからの汎用性・failure rate・3〜5本portfolio結論

H1へ渡せるsuccessor dataは、`source_resolution=640x360`、
`transcript_provider=youtube_subtitles`、`rolling_caption_overlap=21`、
`semantic_duration=33.320s`、`repair_render_elapsed=31.729s`、
`subtitle_authority=source_native_caption_pixels`、`additional_burn_in=false`、
`endpoint_basis=first_scene_transition_after_last_caption_and_speech`、
`http_range/browser_ready=true`、
`human_acceptance=pending`である。H1実装やacceptanceはこのsliceでは行わない。

## 次に進める入口

| 入口 | 解く摩擦 | 選ぶと可能になること | いま必要な条件 |
|---|---|---|---|
| Verify | 修復後exact candidateの字幕リズム・終端・残る違和感を人間が判断 | OUT-09をaccept / reframe / rejectのどれかへ遷移 | 上の一問への回答 |
| Audit | source captionのrolling overlapとword-boundary wrapをsource横断で分類 | 一件専用tuneではないfailure taxonomy | OUT-09回答と追加source data |
| Advance | 3〜5本portfolioへ別source candidateを追加 | repeatabilityの成功率・共通rule・例外を比較 | OUT-09判断、別source承認、同じclosed gates |
| Explore | H1 dataからproduction limitation-lift packetを設計 | render acceptanceとsubtitle design acceptanceを分離 | portfolio evidence。rights/public gateは別owner |

現在の最短の取っ掛かりは`Verify`であり、未回答のまま次sourceを増やしてOUT-09の
品質判断を希釈しない。
