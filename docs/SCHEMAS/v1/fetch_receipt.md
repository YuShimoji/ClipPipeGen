# fetch_receipt.schema (v1)

INT-02 系の素材取得コマンドが、実行内容・生成物・rollback 対象を記録する receipt。INT-02a では `fetch-source-audio --mode fake` が `materials/<material_id>/fetch_receipt.json` を作る。

## 境界

- `fetch_receipt.json` は取得処理の readback と再実行判断のための記録であり、権利判断の正本ではない。
- 権利・出典・利用条件は `rights_manifest.json` と `sidecar.json` に保存する。
- 実 downloader の導入後も、URL / 出力先 / hash / byte size / rollback files を同じ形で残す。
- INT-02b の境界正本は [ASSET_FETCH_BOUNDARY.md](../../ASSET_FETCH_BOUNDARY.md)。yt-dlp / FFmpeg は `asset_fetch` integration に閉じ込め、Editing core / STT / render / GUI には入れない。

## ファイル形式

JSON。INT-02a の配置は `episodes/<episode_id>/materials/<material_id>/fetch_receipt.json`。

## トップレベル構造

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
    "conflicts": [],
    "would_fail_without_force": false
  }
}
```

## 必須フィールド

| フィールド | 型 | 説明 |
|---|---|---|
| `schema_version` | string | 固定値 `"v1"` |
| `episode_id` | string | episode ID |
| `material_id` | string | `material_ledger.materials[].id` と一致 |
| `mode` | string | `fake` / future downloader mode |
| `source_url` | string | 取得元 URL の readback |
| `output_path` | string | 生成された素材ファイル |
| `sha256` | string | 生成ファイルの SHA-256 |
| `byte_size` | number | 生成ファイルのバイトサイズ |
| `created_at` | string | ISO 8601 |
| `rollback.files[]` | string[] | operator が rollback する場合の生成ファイル一覧 |
| `command_summary` | string | 実行コマンドの短い要約 |
| `provider` | string | `asset_fetch_fake` / `yt-dlp` / `local-media` 等 |
| `tools[]` | array | 実 downloader で使った tool 名と version。fake では空配列可 |
| `commands[]` | array | secret を含まない command summary と exit code。fake では空配列可 |
| `input.source_url` | string/null | URL 取得 mode の入力 URL |
| `input.local_path` | string/null | local media mode の入力 file |
| `outputs[]` | array | 生成 file の path / hash / byte size / duration readback |
| `warnings[]` | string[] | fallback、metadata 欠落、duration 不明など |
| `stderr_digest` | string/null | stderr 全文ではなく digest / tail。secret を保存しない |

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

この WAV は ED-07 `transcribe-audio` の `--source-audio` に渡す入力であり、`--material-id` を併用すると `transcript.source_audio.material_id` と `material_ledger` が接続される。

## INT-02b 実 downloader contract

実 downloader は未実装。future mode を追加する場合は、次を守る。

| 領域 | Contract |
|---|---|
| yt-dlp | URL から元 media を取得するだけ。audio normalize / STT / cut / render はしない |
| FFmpeg | source audio を PCM WAV / mono / 16kHz / 16-bit に正規化するだけ。cut / concat / subtitle burn-in / encode はしない |
| output | `materials/<material_id>/source.wav`、`sidecar.json`、`fetch_receipt.json`、`material_ledger` entry |
| readback | command、tool versions、provider/engine、input URL、output paths、duration、hashes、warnings、stderr digest、rollback files |
| rollback | generated file、retained intermediate、sidecar、receipt、ledger material ID の対応関係 |
| boundary | `transcribe-audio` はローカル音声のみを読む。Editing core は FFmpeg / yt-dlp を直接呼ばない |

## CLI

```bash
python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --source-url https://www.youtube.com/watch?v=AAAA \
  --material-id src_audio_001 \
  --mode fake

python -m src.cli.main fetch-source-audio \
  --episode-id episode_example \
  --source-url https://www.youtube.com/watch?v=AAAA \
  --material-id src_audio_001 \
  --mode fake \
  --dry-run
```

`--dry-run` は preflight JSON のみ出力し、ファイルを書かない。既存ファイル・既存 `material_id` は `conflicts[]` と `would_fail_without_force` に表示する。

`--force` は同じ `material_id` の生成物を再生成し、同じ ID の ledger entry を refresh するためのもの。別 `material_id` の ledger entry は削除しない。
