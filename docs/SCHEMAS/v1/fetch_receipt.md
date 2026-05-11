# fetch_receipt.schema (v1)

INT-02 系の素材取得コマンドが、実行内容・生成物・rollback 対象を記録する receipt。`fetch-source-audio` は `materials/<material_id>/fetch_receipt.json` を作る。

## 境界

- `fetch_receipt.json` は取得処理の readback と再実行判断のための記録であり、権利判断の正本ではない。
- 権利・出所・利用条件は `rights_manifest.json` と `sidecar.json` に保持する。
- yt-dlp / FFmpeg は `asset_fetch` integration に閉じ込め、Editing core / STT / render / GUI には入れない。
- 正本: [ASSET_FETCH_BOUNDARY.md](../../ASSET_FETCH_BOUNDARY.md)

## Top-Level 例: fake

```json
{
  "schema_version": "v1",
  "episode_id": "episode_example",
  "material_id": "src_audio_001",
  "mode": "fake",
  "source_url": "https://www.youtube.com/watch?v=AAAA",
  "output_path": "episodes/episode_example/materials/src_audio_001/source.wav",
  "sha256": "abcdef0123...",
  "byte_size": 32044,
  "created_at": "2026-05-10T12:00:00+09:00",
  "rollback": {
    "files": [
      "episodes/episode_example/materials/src_audio_001/source.wav",
      "episodes/episode_example/materials/src_audio_001/sidecar.json",
      "episodes/episode_example/materials/src_audio_001/fetch_receipt.json"
    ],
    "ledger_material_id": "src_audio_001"
  },
  "command_summary": "fetch-source-audio --mode fake",
  "provider": "asset_fetch_fake",
  "tools": [],
  "commands": [],
  "input": {
    "source_url": "https://www.youtube.com/watch?v=AAAA",
    "local_path": null
  },
  "outputs": [
    {
      "path": "episodes/episode_example/materials/src_audio_001/source.wav",
      "sha256": "abcdef0123...",
      "byte_size": 32044,
      "duration_seconds": 1.0
    }
  ],
  "warnings": [],
  "stderr_digest": null,
  "preflight": {
    "schema_version": "v1",
    "episode_id": "episode_example",
    "material_id": "src_audio_001",
    "mode": "fake",
    "source_url": "https://www.youtube.com/watch?v=AAAA",
    "local_media_path": null,
    "local_media_exists": null,
    "output_path": "episodes/episode_example/materials/src_audio_001/source.wav",
    "sidecar_path": "episodes/episode_example/materials/src_audio_001/sidecar.json",
    "receipt_path": "episodes/episode_example/materials/src_audio_001/fetch_receipt.json",
    "material_ledger_path": "episodes/episode_example/material_ledger.json",
    "rights_manifest_path": "episodes/episode_example/rights_manifest.json",
    "audio_format": {
      "container": "wav",
      "codec": "pcm_s16le",
      "sample_rate_hz": 16000,
      "channels": 1,
      "sample_width_bytes": 2,
      "duration_seconds": 1.0
    },
    "will_write": true,
    "command_plan": null,
    "will_call_subprocess": false,
    "conflicts": [],
    "would_fail_without_force": false
  }
}
```

## Top-Level 例: local-media-audio

```json
{
  "schema_version": "v1",
  "episode_id": "episode_example",
  "material_id": "src_audio_local",
  "mode": "local-media-audio",
  "source_url": null,
  "output_path": "episodes/episode_example/materials/src_audio_local/source.wav",
  "sha256": "abcdef0123...",
  "byte_size": 64044,
  "created_at": "2026-05-10T12:00:00+09:00",
  "rollback": {
    "files": [
      "episodes/episode_example/materials/src_audio_local/source.wav",
      "episodes/episode_example/materials/src_audio_local/sidecar.json",
      "episodes/episode_example/materials/src_audio_local/fetch_receipt.json"
    ],
    "ledger_material_id": "src_audio_local"
  },
  "command_summary": "fetch-source-audio --mode local-media-audio",
  "provider": "local-media",
  "tools": [
    {
      "name": "ffmpeg",
      "path": "C:/tools/ffmpeg.exe",
      "path_source": "argument",
      "version": "ffmpeg version 7.1 ..."
    }
  ],
  "commands": [
    {
      "summary": "C:/tools/ffmpeg.exe -y -i input.mov -vn -ac 1 -ar 16000 -sample_fmt s16 -acodec pcm_s16le source.wav",
      "exit_code": 0
    }
  ],
  "input": {
    "source_url": null,
    "local_path": "C:/media/input.mov"
  },
  "outputs": [
    {
      "path": "episodes/episode_example/materials/src_audio_local/source.wav",
      "sha256": "abcdef0123...",
      "byte_size": 64044,
      "duration_seconds": 2.0
    }
  ],
  "warnings": [
    "input duration is not probed in INT-02c; output WAV duration is read after normalization"
  ],
  "stderr_digest": {
    "algorithm": "sha256",
    "sha256": "0123456789abcdef...",
    "tail": "ffmpeg stderr tail after scrub",
    "tail_chars": 800,
    "truncated": false
  }
}
```

## 必須フィールド

| フィールド | 型 | 説明 |
|---|---|---|
| `schema_version` | string | 固定値 `"v1"` |
| `episode_id` | string | episode ID |
| `material_id` | string | `material_ledger.materials[].id` と一致 |
| `mode` | string | `fake` / `local-media-audio` / `yt-dlp-audio` / future mode |
| `source_url` | string/null | URL 取得 mode の readback。`local-media-audio` では `null` |
| `output_path` | string | 生成された素材ファイル |
| `sha256` | string | 生成ファイルの SHA-256 |
| `byte_size` | number | 生成ファイルのバイトサイズ |
| `created_at` | string | ISO 8601 |
| `rollback.files[]` | string[] | operator が rollback する場合の生成ファイル一覧 |
| `rollback.ledger_material_id` | string | rollback 時に消す ledger entry の ID |
| `command_summary` | string | CLI 実行の短い概要 |
| `provider` | string | `asset_fetch_fake` / `local-media` / future `yt-dlp` 等 |
| `tools[]` | array | 実行に使った tool 名、path、path source、version。fake では空配列可 |
| `commands[]` | array | secret を含まない command summary と exit code。fake では空配列可 |
| `input.source_url` | string/null | URL 取得 mode の入力 URL |
| `input.local_path` | string/null | local media mode の入力 file |
| `outputs[]` | array | 生成 file の path / hash / byte size / duration readback |
| `warnings[]` | string[] | fallback、metadata 欠落、duration unknown など |
| `stderr_digest` | object/null | scrubbed stderr の digest / tail。全文 stderr は保存しない |
| `preflight` | object | 実行前 readback。dry-run と同じ形 |

## INT-02a source audio 標準

`fetch-source-audio --mode fake` は、次の標準音声を作る。

| 項目 | 値 |
|---|---|
| ファイル名 | `source.wav` |
| コンテナ | WAV |
| codec | PCM signed 16-bit little-endian |
| channels | mono |
| sample rate | 16 kHz |
| duration | 1 秒 |
| 内容 | silent fixture |
| ledger kind | `source_audio` |
| ledger subkind | `wav_pcm_16k_mono` |
| intended use | `editing_audio` |

この WAV は ED-07 `transcribe-audio` の `--source-audio` に渡せる入力であり、`--material-id` を併用すると `transcript.source_audio.material_id` と `material_ledger` が接続される。

## INT-02c local-media-audio 標準

`fetch-source-audio --mode local-media-audio` は、既存ローカル media file だけを入力にし、FFmpeg で `source.wav` に正規化する。

| 項目 | 値 |
|---|---|
| 入力 | `--local-media <path>`。URL / VOD / network fetch は拒否 |
| FFmpeg discovery | `--ffmpeg-path` → `CLIPPIPE_FFMPEG` → PATH |
| version readback | `ffmpeg -version` の first line。失敗時は実行失敗 |
| normalize command | `-vn -ac 1 -ar 16000 -sample_fmt s16 -acodec pcm_s16le` |
| duration | input duration は probe しない。output WAV duration を Python `wave` で読む |
| stderr | secret scrub 後の SHA-256 と tail のみ receipt に保存 |
| partial failure | partial `source.wav` は削除。sidecar / receipt / ledger は書かない |

## INT-02d / INT-02e yt-dlp-audio receipt contract

INT-02d は spec only。INT-02e では [YTDLP_AUDIO_SPEC.md](../../YTDLP_AUDIO_SPEC.md) に従い、`fetch-source-audio --mode yt-dlp-audio` を source audio URL fetch のみに限定して assistant-side 実装 in_progress。実 URL operator smoke は user-owned URL selection and rights / terms review 待ち。

| 項目 | Contract |
|---|---|
| mode | `yt-dlp-audio` |
| input | `input.source_url` に URL を残し、`input.local_path` は downloaded intermediate ではなく operator input なしを示す |
| provider | yt-dlp extractor / provider readback を保存 |
| tools | `yt-dlp` と `ffmpeg` の path source / version を保存 |
| commands | yt-dlp fetch と FFmpeg normalize を別 command として summary / exit_code 保存 |
| intermediate | downloaded media は一時 file として削除し、`intermediate.retained=false` を保存。ledger 登録しない |
| output | `source.wav` の path / sha256 / byte_size / duration を保存 |
| rights | rights status は snapshot のみ。hard gate にしない |
| stderr | full stderr は保存せず、secret scrub 後の digest / tail のみ |
| rollback | `source.wav`、sidecar、receipt、ledger material ID を対応付ける |
| rights_snapshot | `compliance_status_at_fetch` と `hard_gate=false` を保存する |

URL readback は query / fragment / userinfo を scrub する。実行時には operator が指定した元 URL を yt-dlp に渡すが、`preflight` / `receipt` / `sidecar` / command readback には secret・token・query を残さない。

## CLI

```bash
python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --source-url https://www.youtube.com/watch?v=AAAA \
  --material-id src_audio_001 \
  --mode fake

python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --local-media C:/media/input.mov \
  --material-id src_audio_local \
  --mode local-media-audio \
  --ffmpeg-path C:/tools/ffmpeg.exe

python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --local-media C:/media/input.mov \
  --material-id src_audio_local \
  --mode local-media-audio \
  --ffmpeg-path C:/tools/ffmpeg.exe \
  --dry-run

python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --source-url https://www.youtube.com/watch?v=AAAA \
  --material-id src_audio_url \
  --mode yt-dlp-audio \
  --yt-dlp-path C:/tools/yt-dlp.exe \
  --ffmpeg-path C:/tools/ffmpeg.exe \
  --dry-run
```

`--dry-run` は preflight JSON のみ出力し、ファイルを書かず、FFmpeg / yt-dlp subprocess も network も呼ばない。既存ファイル・既存 `material_id` は `conflicts[]` と `would_fail_without_force` に表示する。

`--force` は同じ `material_id` の生成物を再生成し、同じ ID の ledger entry を refresh するためのもの。別 `material_id` の ledger entry は削除しない。
