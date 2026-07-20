# OUT-10 Third-Source Portfolio Expansion — final utterance endpoint repair

更新日: 2026-07-20

## Outcome

OUT-10は第三distinct source `youtube:TlnviOwLRmk` の同じ冒頭・内容・字幕style・音量方針・
neutral matte構図を維持し、最後の返答だけが未完だった終端を source `30.014s` まで延長した。
stateは `OUT10_FINAL_UTTERANCE_ENDPOINT_REPAIR_READY_FOR_COMBINED_REVIEW`。

人間観測済みの27.711s predecessorは、operation宣言までは完了していたが、その直後から始まる
患者の返答「先生…いけません…打撲です」を含めていなかった。これは
`superseded_predecessor_final_response_incomplete` として未受理lineageに残す。

## Endpoint comparison

| 境界 | 観測 | 判断 |
|---:|---|---|
| 27.711s | 先生側のoperation宣言が完了し、患者の返答が開始する直前 | predecessor; 最終発話不完全 |
| 30.014s | official response cueと音声の最後の音節が完了 | selected |
| 30.033s | 次のshotと無関係な検査dialogueが開始 | 含めない |

selected rangeは `0.000–30.014s`、semantic duration 30.014s、media duration
30.033333s、official JA cue 46。既存45 cueとstyleを変えず、最後の1 cueだけをauthorityに従って
含めた。

## Exact package

package:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | identity |
|---|---|
| candidate MP4 | SHA `a53d0416e17dcc682fa172ca47c7dd268a9dff2cf926bd3c44c6f5a2711134f2`; 16,821,370 bytes |
| readback | SHA `6d3111b7597ac181ae0dc4aa6b9eed76e7865d804388acd475487a343437613b` |
| manifest | file SHA `e27118cc55cc9969feaca3fe9ef595e494fab8c149f3f3386d535b23ae866d6b`; self SHA `2bb1e3abdc303eb65fe300b51afd134a717bea232e00027f57abf409ef0d60cb` |
| endpoint preflight | file SHA `b9ee96edf7edbe4d125fda072b0bd3e8fa59c02cd94e743555a99af2498cc4df` |
| endpoint selection | file SHA `b16b9ee5fc78e534026fb6f5d187243f19f9c814ad4d789d45f1371955f250eb` |
| endpoint evidence manifest | file SHA `195ff30b408ea3a14a52c6d9fec1d7fc4d00b0b0a654b3bdfc981c93ec1fb8ee`; self SHA `f9248f7d4bec7925292e6d8147dd1e12635a9470d5c38036e356e03a71b16585` |

## Validation

- H.264/AAC、1080x1920、30fps、yuv420p、full decode / faststart pass。
- black/silence critical signal QA pass。
- ASS/SRT/readbackは46 cue、final cue end 30.014sで一致。
- full 1920x1080 fit、neutral matte `0x0D1624`、crop/blur/source-derived backgroundなし。
- candidate package全payloadとmanifest self-integrity一致。
- combined packageへコピー後もexact SHA / byte size一致。
- 最終3秒contact sheetでは最後の返答字幕が末尾まで表示され、waveformにも音声欠落なし。

## Human gate

OUT-10単独reviewは閉じ、OUT-11統合reviewの先頭に同じexact MP4を載せる。質問は、最後の
セリフまで一本のShortとして自然に完結したか。肯定・修復・rejectは上記exact SHAにだけbindする。

## Closed gates / Not Done

human acceptance、rights、production render/subtitle/image quality、thumbnail、winner、
public/publishing/upload/OAuth、cross-machine portability、main統合は未承認。
