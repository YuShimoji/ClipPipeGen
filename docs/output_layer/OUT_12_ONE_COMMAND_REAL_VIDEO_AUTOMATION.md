# OUT-12 One-Command Real Video Automation v1

## 到達点

`build-real-video` は、取得済みの実 source MP4 または episode 内 material identity を入力し、
source/provenance解決、content fingerprint、scene/black/silence解析、chronological Timeline IR、
caption timing remap、H.264/AAC render、媒体検証、manifest、localhost review packageを一コマンドで
生成する。失敗時はstageと機械可読な failure stateを残し、成功済み同一入力への`--resume`は
高コストstageを再実行せずmanifestと最終MP4 SHAを再検証する。

実装入口:

- `src/cli/build_real_video.py`
- `src/integrations/render/real_video_pipeline.py`
- `python -m src.cli.main build-real-video --help`

## 実 source run

OUT-11 SOURCE-05の取得済みfull sourceを入力した。preflightした3 sourceのうち、3分以上を満たした
唯一の候補である。requested targetは300秒だが、sourceが260.643991秒のため全sourceを保持し、
scene boundaryで11 cutへ分割した。selection modeは
`full_source_scene_boundary_partition`、semantic sectionsはopening / development / resolutionの3つ。

```powershell
uvx python -m src.cli.main build-real-video `
  --source episodes\out11_source05_dramatic_xviltration_20260720\materials\src_video_out11_source05\source_video.mp4 `
  --authority-readback episodes\out11_source05_dramatic_xviltration_20260720\review\out11_source05_candidate\candidate_readback.json `
  --output-dir episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation `
  --profile long-form --target-duration 300 --force --review-port 8075 --format json
```

| 項目 | 確定値 |
|---|---|
| artifact_id | `clip-out12-one-command-real-video-automation-v1-001` |
| state | `AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1` |
| source | `youtube:gUwJBRUIWow`; SHA `8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf` |
| final_video | 260.693767s、1920x1080、H.264 High / AAC、142,789,781 bytes |
| final SHA-256 | `5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584` |
| edit | 11 cuts、chronology/causal order保持、mapping coverage 1.0 |
| captions | source-native baked captionのみ。timing authorityを468 cueへremapし、重複・負duration・orphan 0。意味、歌唱、歌詞、話者は主張しない |
| render attempts | execution 3、corrective 2。最終passでAV duration delta 0.008767s、true peak -1.44 dBTP |
| manifest | 14 payload、self SHA `8c3929e22c41719ee29a565134ef128ad9a75dde7b83ab9e6cd35a526dd3c489` |

## 検証

媒体検証はshipping codec、source-native 16:9、duration、stream start、monotonic timestamps、
faststart、full decode、AV sync、loudness/true peak、cut間loudness delta、black/silence、caption
containment、source mapping coverageをすべてpassした。packet timestampは32,248件でregression 0、
integrated loudnessは-14.15 LUFS、最大隣接cut差は1.27 LU、最大blackは0.7007s、1秒以上のsilenceは0。

first/middle/last contact sheet、全cut boundary contact sheet、全長waveformを目視した。source由来の
短い暗転はsignal threshold内で、実frameと連続音声が全長に存在する。review pageはHTTP 200、MP4
Range 206、desktop 1280とmobile 390、初期paused/muted/time 0、middle cut seek、media error 0、
console warning/error 0を確認した。mobile表の横はみ出しは生成CSSで修復し、表内部scrollへ閉じた。

## Resume

同じ入力と設定で`--force`を`--resume`へ置き換える。2.095秒で
`content_analysis`、`caption_remap`、`render`、`media_validation`をcache hitとし、
`render_executed=false`、最終MP4 SHA不変、manifest自己整合性一致を返した。入力fingerprintや
manifest payloadが変わった場合はfail closedし、黙って古い出力を再利用しない。

## Review package

- package: `episodes/out12_source05_one_command_real_video_20260721/review/out12_one_command_real_video_automation/`
- launcher: `powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\open_preview.ps1`
- URL: `http://127.0.0.1:8075/review/index.html`
- machine readback: `validation_readback.json`, `run_manifest.json`, `resume_readback.json`

launcher/serverはforegroundで動かし、終了は`Ctrl+C`。検証後のlistenerは残さない。

## 閉じたままのgate

このsliceが受理したのは、一つの実sourceから内部検証可能な長尺MP4と証拠packageを再現する
automation routeである。rightsはpending、production acceptance、production subtitle design、
thumbnail、winner、public/publishing、uploadはfalseのまま。source-native textは保持するが、
sourceの意味内容や使用許諾を自動判定しない。
