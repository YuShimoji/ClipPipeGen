# OUT-09 Second-Source Short Repeatability v0

## 現在の契約

| 項目 | 値 |
|---|---|
| artifact | `clip-out09-second-source-short-repeatability-v0-001` |
| state | `OUT09_ACCEPTED_INTERNAL_CANONICAL_MAIN` |
| branch | `codex/out-09-second-source-short-repeatability-v0` |
| candidate | `candidate_01` |
| source | YouTube `D4i4fjs9PWc` / `【Kroniicle Animation】 Wisdom Teeth Removal Woes` |
| source range | `31.160–64.480s`、semantic `33.320s`、endpointは再openしていない |
| display authority | `generated_short_cue_overlay_from_source_json3` |
| current MP4 | SHA `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`、5,976,722 bytes |
| human state | `human_review_pending=false` / `acceptance_granted=true` / `review_status=accepted_internal` |

目的は、OUT-08とは異なるreal source/episodeでも既存vertical render pathからreviewableな
Shortを再現できるかを確かめること。source固有renderer branchや広範pipeline rewriteは
作らない。current sliceは、人間観測で発覚したserver短命化と大音量自動再生リスクを
review access / presentation safety defectとして直し、同じsource range、主題、candidate
identity、caption、endpoint authority、媒体byteを保つ。

## Stable manual-safe review access

| 面 | 契約 |
|---|---|
| canonical server | `serve_preview.ps1 -Port 8072`を人間が見えるforeground PowerShellで実行し、レビュー中は窓を維持、停止は`Ctrl+C` |
| binding | `127.0.0.1`固定。正しいartifact ID、full MP4 SHA、page 200、Range 206だけをreuse |
| conflict | 未知port ownerを終了しない、alternate portを選ばない |
| human URL | clean `http://127.0.0.1:8072/index.html`; query/hashを付けない |
| playback | `controls playsinline muted preload="metadata"`; autoplayなし、初期paused/muted、volume上限25%、storage復元なし |
| QA | exact `?qa-playback=1`だけをmuted/volume 0で短時間再生してpause。human docs/URLへは渡さない |
| convenience | `open_preview.ps1 -Serve -Port 8072`が別の見えるPowerShellへcanonical serverを起動し、health後にclean URLを開く |
| no-Serve | healthy serverがあればclean URLを開く。なければcanonical commandを表示してexitし、暗黙起動しない |
| access repair | readback/index/opener/server/manifestだけをatomic更新。MP4/ASS/SRTをrender/remux/transcodeしない |

access-only CLIは`repair-second-source-review-access`。既存manifest self/file hashとfixed MP4
SHAを検証し、媒体identityが一致しなければ変更前にfail closedする。

## Human acceptance closure

ユーザーはexact MP4
`b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`について、次をpassした。

- 字幕と音声が一致する
- short cueの切替と可読性が期待どおり
- 初期自動再生・突然の音がない
- foreground server方式でreview accessが維持される
- 終端が発話途中ではなく区切りとして成立する
- overall resultはinternal review用途でaccept

上下のblur/mosaic状canvasは、native caption bandを除外して二重字幕を防ぐsource-specific
処理として今回だけacceptableだった。記録値は
`source_specific_caption_band_suppression_observed_acceptable_not_generalized`。美観、共通design、
caption bandのないsource、cropが重要内容と衝突するsource、production subtitle designへ
一般化しない。別source条件、opaque matte比較、明示production gateでのみ再検討する。

## 人間観測とlineage

前版`3e7ef9d8...2916`は、native captionが中央16:9内で小さく、full-source blurがその
字形を下部canvasへ複製し、下部が霜ガラス状で読めなかった。これは従前のAgent/machine
legibility claimを上書きする。

| lineage index | source range | 字幕/canvas | SHA | 扱い |
|---:|---|---|---|---|
| 0 | `31.160–58.880s` | native + 長文burn-in / full blur | `300ee360...e0c9` | initial predecessor、acceptanceなし |
| 1 | `31.160–64.480s` | 小さいnativeのみ / caption glyphを含むfull blur | `3e7ef9d8...2916` | failed repair、acceptanceなし |
| 2 | `31.160–64.480s` | 27 short cues / caption-free canvas | `b6b90a4b...73da50` | current、accepted internal |

failed reasonは`unreadable_native_caption_and_blurred_caption_duplication`。両predecessorを
plan/readback/manifestへ保持し、判断をcurrent SHAへだけbindする。

## Caption-free canvas

caption-active 10 source framesからsource `640x360`の下部74pxをnative caption bandと
測定した。

| rectangle | pixels | normalized | 使用 |
|---|---|---|---|
| caption-free | `x0 y0 w640 h286` | `0,0,1,0.7944444444` | foregroundとbackground sourceの双方 |
| native caption band | `x0 y286 w640 h74` | `0,0.7944444444,1,0.2055555556` | 双方から除外 |

backgroundはcaption-free cropだけをscale/blurする。full-source blur fallbackは禁止。
fallbackはneutral solidまたはcaption-free edgeだけを許す。10 framesで顔・人物・主動作を
維持し、crop conflictはnone、maskは不使用。重要内容と衝突した場合にだけopaque matteを
次候補とするが、今回のrenderでは使っていない。

shared `vertical_short_candidate`は任意`composition_policy`を受け取る。未指定時のfilterは
従来どおりで、OUT-05/06/08のdefault behaviorを変えない。明示policyはsource dimension、
crop、caption band非交差、bottom crop整合、fallback、frosted surface禁止をrender前に
fail-closed validationする。

## Short-cue subtitle authority

YouTube English Original JSON3のevent startとtoken offsetをtiming authorityとし、
raw eventの長文を1–6語の短いcueへ分割した。

| 指標 | 値 |
|---|---:|
| cue count | 27 |
| word count | min 1 / max 6 |
| line count | min 1 / max 2 |
| duration | min 0.48s / max 2.36s |
| whole-word wrap | true |
| timing gaps | max 0.15s以下 |
| final cue | `So.`、`30.840–33.200s` |

ASS/SRTの27 cueが表示兼provenance authorityで、動画へburn-inする。source-native caption
pixelsはbottom cropで抑止する。字幕はopaque solid black plate、crisp outline/shadow。
transparent blur、frosted plate、blurred glyph carrierは使わない。

## Endpoint authority

今回のpresentation repairではendpointを再openしていない。既存evidence:

- last native caption end: `64.360s`
- last speech end: `64.362812s`
- silence end: `64.541125s`
- next scene / next native caption start: `64.480s`
- selected end-exclusive boundary: `64.480s`

fixed padding、fade、SFX、freeze、追加silenceはなし。candidate start `31.160s`も維持する。

## Package

ignored package:

`episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/`

| file/evidence | 値 |
|---|---|
| `candidate_01.mp4` | H.264 High/AAC LC、1080x1920、30fps、yuv420p、33.333008s |
| `candidate_01_subtitles.ass/.srt` | 27 Dialogue/cues、display + provenance |
| `candidate_01_frame_qa.jpg` | 10 samples、SHA `792f6b2f...9901` |
| `candidate_01_navigation.jpg` | SHA `1df89d1f...156d`、navigation-only、thumbnail acceptanceではない |
| plan input | SHA `569ba9d193348d76ee368dde32ebd7c00c485a03792b4728562efec452b00c7e` |
| manifest | 10 package files、self `50ff14e5ee9ffae0ab1cb31f33a584c346026d7674c360546302e10de24e62ff` |
| ASS/SRT SHA | `03df9259d8b9c56b532477187d9990a73c0d847b1659420ffed4c926220b9ea9` / `de1290f236e556fbd7a2159c43c86c01e455990e9cefb19c7e822fc2b1cb016f`、access修復前後で不変 |
| render count | corrective 1、additional 0、builder 32.904s、outer 33.498s |

`episodes/`はignoredで、Gitにcopyrighted pixelsを追加しない。packageは同一マシン証跡で
あり、別cloneでのavailabilityやportabilityを主張しない。

## Validation

| 検証 | 結果 |
|---|---|
| media | full decode exit 0、faststart passed、1 video + 1 audio |
| loudness | input `-27.77 LUFS / -6.87 dBTP`、output `-14.80 LUFS / -1.46 dBTP` |
| signal | blackdetect event 0、silencedetect event 0 |
| frame | 10点でnative caption/blur glyph/frosted surfaceなし、short cueと重要内容を確認 |
| HTTP | page 200、MP4 Range 206、Content-Range/Length一致、3 probeを54秒超にわたり通過 |
| server lifecycle | browser close/reopen中も維持、correct double-start reuse、unknown owner reject/owner生存、Ctrl+C後8072/8074 listener 0 |
| browser human | clean URLは2.1秒後もpaused/muted/currentTime 0、manual Space playでcurrentTime前進、close/reopenで初期状態へ復帰 |
| browser QA | exact QA queryだけがmutedで約1.08秒進行後pause、clean URLへ戻すとcurrentTime 0 |
| responsive | default / 375px級ともhorizontal overflow false、question count 2 |
| console | warn/error 0 |
| direct consumers | review Range server / OUT-09 / current-state / dashboard / shared renderer consumersは`81 passed, 2 deselected`。既知OUT-06 2件はbase/branch比較へ分離 |
| PowerShell | generated opener/server parse 0 error |
| Ruff | changed Python/test files passed |

full repository pytestとGUI/Electronはvalidation budget外で実行していない。既存OUT-06
wrap expectationは別監査事項で、OUT-09を広げて直していない。

## Historical review entrypoint

canonical foreground route:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\serve_preview.ps1 -Port 8072
```

convenience route:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Serve -Port 8072
```

URL: `http://127.0.0.1:8072/index.html`。review pageはcurrent MP4/poster SHAをqueryへ含み、
acceptance前は次の二つを表示した。

1. ページを開いた直後に動画や音が勝手に始まらず、レビュー中にserverが維持されるか。
2. 手動で再生・音声解除した後、字幕の切替・可読性・終わり方に明確な違和感があるか。

## Rebuild command

媒体を変えずreview accessだけを再構成するcommand:

```powershell
uvx python -m src.cli.main repair-second-source-review-access --output-dir episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability --format json
```

媒体buildは別routeであり、access defectだけのために実行しない:

```powershell
uvx python -m src.cli.main build-second-source-short-repeatability `
  --episode-dir episodes\holoen01_kronii_wisdomteeth_out09_20260718 `
  --output-dir episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability `
  --candidate-plan-input episodes\holoen01_kronii_wisdomteeth_out09_20260718\out09_candidate_plan_input.json `
  --ffmpeg C:\Users\thank\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffmpeg.exe `
  --ffprobe C:\Users\thank\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0.1-full_build\bin\ffprobe.exe `
  --format json
```

上記absolute tool pathは同一マシン実行例で、portable dependencyを意味しない。今回の
契約render budgetは消費済みのため、human reviewまたはobjective failureなしに再実行しない。

## Evidence boundary

証明済みなのは、特定のdifferent sourceで、caption-free crop、JSON3 short cues、既存
vertical rendererを組み合わせ、1本のtechnically reviewable Shortを作れることまで。
未証明:

- current exact MP4のhuman creative acceptance
- YouTube caption全文のhuman transcript acceptance
- 640x360 sourceのproduction画質
- caption band detectorやcrop ruleのsource横断一般化
- physical phone / low-end deviceでの判読性・performance
- rights/material use、production subtitle/render、thumbnail、public/publishing/upload
- ignored packageのcross-machine portability

OUT-10 successorへdata-onlyで渡せるのは、source resolution、crop/band rectangles、10 frame
measurement、27 cue統計、JSON3 timing authority、render duration、media/browser結果、
lineage、exact internal acceptance、source-specific suppression非一般化という事実だけである。

次候補は`OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION`。本contractではdata-onlyで、未実装。
