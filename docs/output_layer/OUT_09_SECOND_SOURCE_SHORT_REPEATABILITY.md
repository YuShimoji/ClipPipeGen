# OUT-09 Second-Source Short Repeatability v0

## 現在の契約

| 項目 | 値 |
|---|---|
| artifact | `clip-out09-second-source-short-repeatability-v0-001` |
| state | `OUT09_CLEAR_SHORT_CUE_CAPTION_PRESENTATION_REVIEW_READY` |
| branch | `codex/out-09-second-source-short-repeatability-v0` |
| candidate | `candidate_01` |
| source | YouTube `D4i4fjs9PWc` / `【Kroniicle Animation】 Wisdom Teeth Removal Woes` |
| source range | `31.160–64.480s`、semantic `33.320s`、endpointは再openしていない |
| display authority | `generated_short_cue_overlay_from_source_json3` |
| current MP4 | SHA `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`、5,976,722 bytes |
| human state | `human_review_pending=true` / `acceptance_granted=false` |

目的は、OUT-08とは異なるreal source/episodeでも既存vertical render pathからreviewableな
Shortを再現できるかを確かめること。source固有renderer branchや広範pipeline rewriteは
作らない。current sliceは、人間観測で発覚したcaption presentation欠陥だけを直し、同じ
source range、主題、candidate identity、endpoint authorityを保つ。

## 人間観測とlineage

前版`3e7ef9d8...2916`は、native captionが中央16:9内で小さく、full-source blurがその
字形を下部canvasへ複製し、下部が霜ガラス状で読めなかった。これは従前のAgent/machine
legibility claimを上書きする。

| lineage index | source range | 字幕/canvas | SHA | 扱い |
|---:|---|---|---|---|
| 0 | `31.160–58.880s` | native + 長文burn-in / full blur | `300ee360...e0c9` | initial predecessor、acceptanceなし |
| 1 | `31.160–64.480s` | 小さいnativeのみ / caption glyphを含むfull blur | `3e7ef9d8...2916` | failed repair、acceptanceなし |
| 2 | `31.160–64.480s` | 27 short cues / caption-free canvas | `b6b90a4b...73da50` | current、human review pending |

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
| manifest | 10 files / 6 inputs、self `fec262226982bab5f650b954efb121f646d19d054896cf93a0e1098ccaba1aa7` |
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
| HTTP | root 200、MP4 Range 206 |
| browser | readyState 4、error null、duration 33.333008、1080x1920、play/pause successful |
| responsive | default / 375px級ともhorizontal overflow false、question count 1 |
| console | warn/error 0 |
| OUT-09 tests | 13 passed |
| shared direct consumers | 33 passed / 2 OUT-06 reviewed-wrap tests deselected |
| Ruff | changed renderer/test files passed |

full repository pytestとGUI/Electronはvalidation budget外で実行していない。2 deselectedは
既存OUT-06 wrap expectationの別監査事項で、OUT-09を広げて直していない。

## Review entrypoint

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

URL: `http://127.0.0.1:8072/index.html`

review pageはcurrent MP4/poster SHAをqueryへ含み、質問を次の一つだけ表示する。

1. 字幕が短い単位で自然に切り替わり、画面を邪魔せず読めるか。最後の終わり方を含め、ほかに明確な違和感があれば教えてください。

## Rebuild command

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

H1 successorへdata-onlyで渡せるのは、source resolution、crop/band rectangles、10 frame
measurement、27 cue統計、JSON3 timing authority、render duration、media/browser結果、
lineage、human acceptance pendingという事実だけである。
