# fetch_receipt.schema (v1)

INT-02 系の素材取得コマンドが、実行内容・生成物・rollback 対象を記録する receipt。INT-02a では `fetch-source-audio --mode fake` が `materials/<material_id>/fetch_receipt.json` を作る。

## 境界

- `fetch_receipt.json` は取得処理の readback と再実行判断のための記録であり、権利判断の正本ではない。
- 権利・出典・利用条件は `rights_manifest.json` と `sidecar.json` に保存する。
- 実 downloader の導入後も、URL / 出力先 / hash / byte size / rollback files を同じ形で残す。

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
