# tiny_render artifacts (OUT-01 / OUT-01a)

OUT-01 は `source_video` material、`source_audio` material、`edit_pack.json` の selected cut を接続し、確認可能な短い動画 artifact を生成する plumbing proof。production render、creative acceptance、subtitle burn-in、publishing ではない。

OUT-01a は同じ artifact 生成経路を保ったまま、render 前 preflight、codec/container fallback readback、failure classification を追加する。成功判定は `rendered_video.*` の再生成を含み、docs / taxonomy だけでは done にしない。

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
- `--dry-run`

## Timeline policy

`render-tiny-proof` は `edit_pack.selected_cut_ids[0]` を優先し、無い場合は最初の `cut_candidates[0]` を使う。

初回 proof の policy は固定:

- loop しない
- speed change しない
- complex concat しない
- subtitle burn-in しない
- source video / source audio / `--duration-sec` のうち最短の利用可能 range に clamp する

clamp、duration target unmet、source video/audio duration mismatch は `timeline_mapping.warnings[]` と top-level `warnings[]` に残す。

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
| `ffmpeg_command_failed` | FFmpeg command が上記以外で失敗 |
| `metadata_probe_failed` | render 後の FFprobe metadata readback が失敗 |
| `code_bug_or_unexpected_exception` | 予期しない例外 |

`mp4 / libx264 / aac` を第一候補とし、auto profile では同 container の alternate codec、必要時は `mkv` profile を fallback 候補として持つ。実際に試した profile は `attempted_render_profiles[]` に status と failure reason を残す。未試行候補は `preflight.command_plan.render_profiles[]` に残る。

## Boundary

OUT-01 は diagnostic output proof に限定する。次は別 slice として扱う:

- production render / full render pipeline
- subtitle burn-in
- font / safe area / layout polish
- source-video URL acquisition
- GUI render button
- YouTube upload / publishing
- NLE XML export

