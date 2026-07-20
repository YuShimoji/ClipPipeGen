# OUT-10 Third-Source Portfolio Expansion — human-review endpoint repair

更新日: 2026-07-21

## 到達状態

第三distinct source `youtube:TlnviOwLRmk` の成立済み導入・主題・字幕style・音量方針・
neutral matte構図を維持し、人間レビューで未完と判定された終端だけを修復した。stateは
`OUT10_HUMAN_REVIEW_ENDPOINT_REPAIR_READY_FOR_COMBINED_REVIEW`。

旧exact MP4 `a53d0416e17dcc682fa172ca47c7dd268a9dff2cf926bd3c44c6f5a2711134f2`
（16,821,370 bytes、source `0.000–30.014s`）は、導入自体は成立していたが、直後に始まる
意識確認場面が途中で終わり、自然なsemantic closureになっていなかった。この人間判断を
`superseded_human_review_new_examination_scene_did_not_naturally_close`としてlineageへ固定した。

## 終端の選択

| 境界 | 実内容 | 判断 |
|---:|---|---|
| 30.014s | 「意識確認、開始」が始まり、新しい診察反応が進行中 | 旧候補の未完終端 |
| 31.749–33.584s | 「大丈夫ですか」「息してますか」と患者反応が継続 | 途中なので採用しない |
| 34.785s | 「ゴッドハンドやね」のパンチラインと反応が完了 | selected |
| 34.800s | 別キャラクター紹介のvisual/dialogueが開始 | 含めない |

selected rangeは`0.000–34.785s`、semantic duration 34.785s、media duration 34.800s。
旧46 cueを変えず、同じofficial JA JSON3 authorityから4 cueを追加して計50 cueとした。

## Exact package

package:
`episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/`

| artifact | exact identity |
|---|---|
| candidate MP4 | SHA `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd`; 19,319,488 bytes |
| readback | SHA `77e6c578580d66349b8a94ec5bbadef8d1ca42e3d7fde7faee5debfd35175c53` |
| manifest | file SHA `093d7355c16df01aafb099c24a643183c13a11263ba9d9ebc6d1dfc041d71e80`; self SHA `e1113ae94d7586de2b1f251c38d4479484c0cb67b31bdfd260bd1ed116d4abc2` |
| endpoint evidence | preflight payload SHA `774ac9df...60406`; selection SHA `de1424bf...15f5`; evidence manifest file SHA `937b142d...3b2c` |

## 検証

- 修復renderは事前観測後の1回だけ。corrective pass 0、build 149.147秒。
- H.264/AAC、1080x1920、30fps、yuv420p、full decode、faststart pass。
- `-13.79 LUFS / -1.45 dBTP`、blackdetect 0、silencedetect 0。
- subtitle containmentは50 cueすべてpass、最大3行、最終cue end 34.785s。
- full 1920x1080 fit、neutral matte `0x0D1624`、crop/blur/source-derived backgroundなし。
- 最終6秒contact sheetで意識確認から最終パンチラインへの連続動作、waveformで終端までの
  音声継続を確認した。別sceneの先頭を数frame付加して区切りにしていない。
- package全payload hashとmanifest self-integrity、OUT-11へのexact byte copyが一致。

## 残る人間判断と閉じたgate

OUT-11統合reviewで、意識確認・患者反応・最終台詞まで自然に閉じ、成立済みの導入・字幕・
音声・構図に回帰がないかだけを確認する。回答は新SHAにのみbindする。

human acceptance、rights、production render/subtitle/image quality、thumbnail、winner、
public/publishing/upload/OAuth、cross-machine portability、main統合は未承認。
