# tiny_render artifacts (OUT-01 / OUT-01a / OUT-01b / OUT-01c / OUT-01d)

OUT-01 は `source_video` material、`source_audio` material、`edit_pack.json` の selected cut を接続し、確認可能な短い動画 artifact を生成する plumbing proof。production render、creative acceptance、publishing ではない。

OUT-01a は同じ artifact 生成経路を保ったまま、render 前 preflight、codec/container fallback readback、failure classification を追加する。成功判定は `rendered_video.*` の再生成を含み、docs / taxonomy だけでは done にしない。

OUT-01b は同じ artifact schema を使い、10〜30 秒程度の local source video / source audio / selected cut smoke を扱う。目的は duration target、clamp、stream mismatch、timeline mapping を診断できる長さへ進めることであり、URL video acquisition、subtitle burn-in、GUI render button、production render へは進まない。

OUT-01c は `render-tiny-proof --burn-in-subtitles diagnostic` で、既存 `edit_pack.subtitles[]`（無い場合は sibling `transcript.json` segments）を UTF-8 SRT に変換し、diagnostic overlay として動画フレーム上へ焼き込む。目的は subtitle artifact の由来を保持したまま visual artifact に接続できることを確認することであり、typography / safe-area / line-wrap / font polish / creative acceptance ではない。

既定の出力先は `episodes/<episode_id>/renders/<output_id>/`。

| artifact | purpose |
|---|---|
| `rendered_video.mp4` / `rendered_video.mkv` | diagnostic rendered video artifact。mp4/H.264/AAC を優先し、環境により mkv を許可する |
| `render_receipt.json` | 実行 command、FFmpeg/FFprobe preflight/version、attempted render profiles、selected profile、failure classification、input refs、timeline mapping、warnings、output metadata を保存する |
| `render_manifest.json` | operator / CI が読む readback。source refs、timeline policy、profile/fallback paths、output paths、output metadata、non-production warnings を保持する |
| `render_report.html` | 人間が確認する小さな HTML report。input refs、timeline mapping、metadata、selected profile、attempts、warnings を表示する |

## CLI

```powershell
python -m src.cli.main render-tiny-proof `
  --episode-id ep_x `
  --root episodes `
  --source-video-material-id src_video_001 `
  --source-audio-material-id src_audio_001 `
  --edit-pack-path episodes/ep_x/edit_pack.json `
  --output-id out01_tiny_render `
  --duration-sec 10
```

Optional:

- `--container mp4|mkv`
- `--video-codec auto|<ffmpeg codec>`
- `--audio-codec auto|<ffmpeg codec>`
- `--ffmpeg-path`
- `--ffprobe-path`
- `--burn-in-subtitles off|diagnostic`
- `--dry-run`

## Timeline policy

`render-tiny-proof` は `edit_pack.selected_cut_ids[0]` を優先し、無い場合は最初の `cut_candidates[0]` を使う。

初回 proof の base policy は固定:

- loop しない
- speed change しない
- complex concat しない
- default では subtitle burn-in しない
- `--burn-in-subtitles diagnostic` の場合だけ、既存 subtitle source を diagnostic overlay として焼き込む
- source video / source audio / `--duration-sec` のうち最短の利用可能 range に clamp する

clamp、duration target unmet、source video/audio duration mismatch は `timeline_mapping.warnings[]` と top-level `warnings[]` に残す。

## OUT-01b longer local smoke readback

OUT-01b は schema を増やさず、既存 field に次を読める状態を要求する:

- local `source_video` material の duration / container / video codec / audio codec / resolution / fps / stream count
- `source_audio` material の duration / WAV codec / sample rate / channels
- `edit_pack` selected cut id と requested range
- timeline policy、duration target、render start、render duration、clamp 有無、warning
- FFmpeg / FFprobe preflight、attempted profiles、selected profile、fallback 有無
- rendered output の duration / container / video codec / audio codec / resolution / fps / stream count

10 秒以上の output duration を目標にし、未達時は `duration target unmet` warning と理由を残す。fixture / synthetic input を使う場合は diagnostic fixture として扱い、`production_candidate=false`、`creative_acceptance=false`、`publish_acceptance=false` を維持する。

## OUT-01c subtitle burn-in diagnostic readback

OUT-01c は schema を少し広げ、subtitle source と overlay 方針を receipt / manifest / report に残す:

- `subtitle_burn_in.status`: `disabled` / `enabled` / `failed`。default は `disabled`。diagnostic mode 成功時のみ `enabled`
- `subtitle_burn_in.source_ref.source_type`: `edit_pack_subtitles` を優先。無い場合は `transcript_segments_diagnostic`
- `subtitle_burn_in.source_ref.path`: `edit_pack.json` または `transcript.json`
- `subtitle_burn_in.source_ref.subtitle_ids[]` / `source_segment_ids[]`: 実際に焼き込んだ subtitle / transcript segment の ID
- `subtitle_burn_in.source_ref.subtitle_file`: render output directory 内の generated `diagnostic_subtitles.srt`
- `subtitle_burn_in.items[]`: rendered timeline 上の start/end、source timeline 上の start/end、text、cut_id、source_segment_id
- `subtitle_overlay_policy`: `position=bottom_center_fixed`、FFmpeg subtitles filter の default font provider、source timeline から rendered timeline への clamp、既存改行保持、line-wrap / typography / safe-area polish をしないこと
- `outputs.diagnostic_subtitle_file`: generated SRT の path

明示 `--burn-in-subtitles diagnostic` で subtitle source が無い場合は silent fallback せず失敗する。FFmpeg `subtitles` filter / font / libass 由来の失敗は `subtitle_filter_failed` として分類し、render が成功しても `production_candidate=false` / `creative_acceptance=false` / `publish_acceptance=false` を維持する。

## OUT-01d subtitle timing / font-filter diagnostic readback

OUT-01d は OUT-01c の diagnostic overlay を production design に広げず、subtitle timing / font-filter preflight の readback を固める。

- `subtitle_burn_in.status`: `disabled` / `enabled` / `failed` / `skipped`。`skipped` は subtitle source は見つかったが render window に書ける item が無い状態
- `subtitle_burn_in.items[]`: `original_start_seconds` / `original_end_seconds`、`render_start_seconds` / `render_end_seconds`、互換用 `source_start_seconds` / `source_end_seconds` / `start_seconds` / `end_seconds`、`status`、`render_start_offset_seconds`、`skip_reason`、text、cut_id、source_segment_id を持つ
- `subtitle_burn_in.timing_mapping`: source timeline から render timeline へ `render_start_offset_seconds` を差し引き、overlap を clamp し、window 外 / invalid / empty を skip する policy。`render_window`、`status_counts`、`renderable_item_count`、`skipped_item_count` を持つ
- `subtitle_burn_in.filter_preflight`: FFmpeg `subtitles` filter availability は render attempt に委ねる。成功時は `passed_by_successful_render`、失敗時は `subtitle_filter_failed` と `failure_detail`、SRT write は `srt_encoding.status=written`、path escaping 方針は `path_escaping.strategy` に残す
- Timing status は `included`、`clamped_to_render_window`、`skipped_before_render_window`、`skipped_after_render_window`、`invalid_timing`、`empty_text` のいずれか。SRT に書くのは `included` / `clamped_to_render_window` のみで、skipped / invalid / empty は report から診断できるよう readback に残す
- Failure detail は `ffmpeg_subtitles_filter_missing`、`libass_failure`、`fontconfig_failure`、`font_provider_failure`、`srt_encoding_or_parsing_failure`、`subtitle_file_path_or_escaping_failure`、`ffmpeg_subtitles_filter_failure` を使う。これは typography / font choice / safe-area polish ではなく、環境差と filter failure の診断用

## Manifest minimum

`render_manifest.json` は少なくとも次を持つ:

- `artifact_kind="tiny_render_proof"`
- `format="tiny_render_proof_v1"`
- `production_candidate=false`
- `creative_acceptance=false`
- `publish_acceptance=false`
- `status`
- `failure_classification.status`
- `failure_classification.failure_reason`
- `source_refs.source_video`
- `source_refs.source_audio`
- `source_refs.edit_pack`
- `source_refs.transcript`
- `timeline_mapping`
- `subtitle_burn_in.status`
- `subtitle_burn_in.source_ref`
- `subtitle_burn_in.timing_mapping`
- `subtitle_burn_in.filter_preflight`
- `subtitle_overlay_policy`
- `preflight.tool_preflight.ffmpeg.available`
- `preflight.tool_preflight.ffmpeg.path`
- `preflight.tool_preflight.ffprobe.available`
- `preflight.tool_preflight.ffprobe.path`
- `selected_render_profile.profile_id`
- `selected_container`
- `selected_video_codec`
- `selected_audio_codec`
- `attempted_render_profiles[]`
- `fallback_used`
- `outputs.rendered_video`
- `outputs.render_receipt`
- `outputs.render_manifest`
- `outputs.render_report`
- `output_metadata.duration_seconds`
- `output_metadata.container`
- `output_metadata.video_codec`
- `output_metadata.audio_codec`
- `output_metadata.resolution`
- `output_metadata.fps`
- `output_metadata.stream_count`
- `warnings[]`

## OUT-01a failure classification

Failure は最低限この分類に寄せる:

| reason | 意味 |
|---|---|
| `environment_missing_ffmpeg` | FFmpeg が discovery / version preflight を通らない |
| `environment_missing_ffprobe` | FFprobe が discovery / version preflight を通らない |
| `codec_or_container_unsupported` | codec / muxer / container 指定が環境で使えない |
| `input_video_missing` | source video path が存在しない |
| `input_audio_missing` | source audio path が存在しない |
| `input_stream_invalid` | 入力 stream が壊れている、または必要 stream が読めない |
| `duration_or_timeline_mismatch` | duration / timeline が非正値または利用不能 |
| `subtitle_source_missing` | diagnostic subtitle burn-in が要求されたが、subtitle file / source が存在しない |
| `subtitle_filter_failed` | FFmpeg `subtitles` filter、libass、font provider、filtergraph escaping など subtitle overlay で失敗 |
| `subtitle_srt_encoding_failed` | diagnostic SRT の UTF-8 write / encoding が失敗 |
| `subtitle_srt_write_failed` | diagnostic SRT file の書き込みが失敗 |
| `ffmpeg_command_failed` | FFmpeg command が上記以外で失敗 |
| `metadata_probe_failed` | render 後の FFprobe metadata readback が失敗 |
| `code_bug_or_unexpected_exception` | 予期しない例外 |

`mp4 / libx264 / aac` を第一候補とし、auto profile では同 container の alternate codec、必要時は `mkv` profile を fallback 候補として持つ。実際に試した profile は `attempted_render_profiles[]` に status と failure reason を残す。未試行候補は `preflight.command_plan.render_profiles[]` に残る。

## Boundary

OUT-01 は diagnostic output proof に限定する。次は別 slice として扱う:

- production render / full render pipeline
- production subtitle burn-in / subtitle design acceptance
- font / safe area / layout polish
- source-video URL acquisition
- GUI render button
- YouTube upload / publishing
- NLE XML export
