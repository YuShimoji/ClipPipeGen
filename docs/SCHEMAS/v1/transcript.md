# transcript.schema (v1)

Speech-to-text の出力 artifact。ローカル音声ファイルを `transcribe-audio` で読み、発話セグメントと実行 readback を `transcript.json` として保存する。

この schema は ED-07 の正本であり、ED-04（字幕案生成）、ED-02（自動 cut 候補抽出）、ED-03（文脈チェック）が入力として参照する。

## 境界

- `transcribe-audio` は **既存のローカル音声ファイル**を入力にして `transcript.json` を生成する。
- VOD / URL からの音声・動画取得は `transcribe-audio` に含めない。取得は INT-02 `asset_fetch`（`fetch-source-audio` / `fetch-source-video`）の責務。
- ED-07 初期の `fake` engine は fixture / deterministic test 用に残す。ED-07b では optional provider として `vosk` adapter を追加し、明示された model path で実 `source.wav` から transcript を生成できる。provider / model が無い場合は preflight failure にし、fixture へ fallback しない。
- ED-07c では Vosk model path の basename から言語を推定できる場合に `--language` と照合する。推定できる不一致は dry-run / actual とも失敗し、推定不能な model 名は warning に留める。
- source audio の rights / sidecar / ledger 情報は readback と判断材料であり、値だけで transcript 生成を止める hard gate にはしない。

## ファイル形式

JSON。配置は `episodes/<episode_id>/transcript.json`。

## トップレベル構造

```json
{
  "schema_version": "v1",
  "episode_id": "episode_example",
  "created_at": "2026-05-08T12:00:00+09:00",
  "updated_at": "2026-05-08T12:00:00+09:00",
  "language": "ja",
  "source_audio": {
    "path": "episodes/episode_example/materials/audio/source.wav",
    "material_id": "src_audio_001",
    "sha256": "0123456789abcdef",
    "duration_seconds": 3600.0,
    "sample_rate_hz": 48000,
    "channels": 2
  },
  "stt": {
    "engine": "vosk",
    "provider": "vosk",
    "engine_version": "unknown",
    "model": "_tmp/stt_models/vosk-model-small-ja-0.22",
    "params": {
      "language": "ja",
      "model_path": "_tmp/stt_models/vosk-model-small-ja-0.22",
      "language_model_check": "passed",
      "model_language": "ja",
      "word_timing": true
    },
    "started_at": "2026-05-08T12:00:00+09:00",
    "completed_at": "2026-05-08T12:10:00+09:00",
    "warnings": [],
    "real_transcript": true,
    "segment_count": 1
  },
  "segment_count": 1,
  "segments": [
    {
      "id": "seg_000001",
      "start_seconds": 12.34,
      "end_seconds": 15.67,
      "text": "ここが一番おもしろいところ",
      "confidence": 0.91,
      "speaker": null,
      "review_status": "unreviewed",
      "notes": []
    }
  ],
  "review": {
    "status": "draft",
    "reviewed_by": null,
    "reviewed_at": null,
    "notes": []
  }
}
```

## フィールド定義

### `source_audio`

STT に渡したローカル音声ファイルの readback。

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `path` | string | ✓ | repo root からの相対パス、または operator が指定したローカルパス |
| `material_id` | string/null | optional | `material_ledger` に登録済みならその ID |
| `sha256` | string | optional | 入力音声の hash。再実行・receipt 照合用 |
| `duration_seconds` | number | optional | 入力音声の長さ |
| `sample_rate_hz` | number | optional | サンプルレート |
| `channels` | number | optional | チャンネル数 |

### `stt`

実行した STT engine と readback。provider 固有値は `params` に閉じ込める。fake / fixture 由来か、実音声から生成された transcript かは `real_transcript` で readback する。

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `engine` | string | ✓ | `fake` / `vosk` / future `whisper.cpp` 等 |
| `provider` | string | optional | provider readback。未指定なら `engine` と同じ |
| `engine_version` | string | optional | 実行 engine の version。取得不能なら `unknown` |
| `model` | string | optional | 使用 model 名または model path |
| `params` | object | optional | language、beam size、temperature 等の engine 固有引数 |
| `started_at` | string | optional | ISO 8601 |
| `completed_at` | string | optional | ISO 8601 |
| `warnings` | string[] | optional | engine warning / fallback なしで継続した注意点 |
| `real_transcript` | boolean | optional | 実音声由来なら `true`。fake / fixture は `false` |
| `segment_count` | number | optional | `segments[]` 件数の readback |

### `segments[]`

```json
{
  "id": "seg_000001",
  "start_seconds": 12.34,
  "end_seconds": 15.67,
  "text": "ここが一番おもしろいところ",
  "confidence": 0.91,
  "speaker": null,
  "review_status": "unreviewed",
  "notes": []
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✓ | episode 内で一意。`seg_<seq>` 推奨 |
| `start_seconds` | number | ✓ | 入力音声上の開始秒 |
| `end_seconds` | number | ✓ | 入力音声上の終了秒。`start_seconds < end_seconds` 必須 |
| `text` | string | ✓ | STT 結果本文。空文字禁止 |
| `confidence` | number/null | optional | 0.0〜1.0。engine が返さない場合は null |
| `speaker` | string/null | optional | 話者推定がある場合のみ |
| `review_status` | enum | ✓ | `unreviewed` / `accepted` / `needs_fix` / `rejected` |
| `notes` | string[] | optional | STT 誤り、固有名詞、聞き取りメモ |

### `review`

transcript 全体の operator review 状態。

`status` 候補: `draft` / `needs_review` / `approved` / `rejected`

`status == "approved"` の場合、`reviewed_by` と `reviewed_at` が必須。

## バリデーション規則

1. `schema_version == "v1"`
2. `episode_id` / `created_at` / `updated_at` / `language` 必須
3. `source_audio.path` 必須
4. `stt.engine` 必須
5. `segments[]` は配列。空の場合は `stt.warnings[]` または `review.notes[]` に理由を残し、downstream は `manual_needed` 相当として扱う
6. `segments[].id` は一意
7. `segments[].start_seconds < segments[].end_seconds`
8. `segments[].start_seconds` / `end_seconds` は負数不可
9. `segments[].text` は空文字禁止
10. `segments[]` は原則として時系列順。重なりは `review.notes` で説明する
11. `segments[].review_status in {"unreviewed","accepted","needs_fix","rejected"}`
12. `review.status == "approved"` の場合、`reviewed_by` / `reviewed_at` 必須

## Downstream

- ED-04 は `generate-subtitles` で `segments[]` を subtitle draft に変換し、ED-05 の表示幅計測を使って `edit_pack.subtitles[].text` に折返しを入れる。
- ED-02 は `generate-cuts` で `segments[]` の時間範囲・密度・topic hint を使って `edit_pack.cut_candidates[]` を生成する。
- ED-03 は cut 前後の隣接 segment を見て、文脈切断や話者発話の途切れを review note として返す。

## CLI（ED-07）

```bash
python -m src.cli.main transcribe-audio \
  --episode-id episode_example \
  --source-audio samples/episode_example/materials/audio/source.wav \
  --output samples/episode_example/transcript.json \
  --language ja \
  --engine fake \
  --fixture-segments samples/episode_example/fixture_segments.json

uvx --with vosk python -m src.cli.main transcribe-audio \
  --episode-id episode_example \
  --source-audio episodes/episode_example/materials/src_audio_001/source.wav \
  --output episodes/episode_example/transcript.json \
  --language ja \
  --engine vosk \
  --model _tmp/stt_models/vosk-model-small-ja-0.22 \
  --material-ledger episodes/episode_example/material_ledger.json \
  --material-id src_audio_001

python -m src.cli.main validate-transcript \
  --transcript samples/episode_example/transcript.json \
  --format json

python -m src.cli.main review-transcript \
  --transcript episodes/episode_example/transcript.json \
  --patch episodes/episode_example/transcript_review_patch.json \
  --reviewed-by user:operator \
  --dry-run \
  --format json
```

`fake` engine は fixture segments を読み、ローカル音声ファイルの存在確認・sha256・STT readback を付けて transcript を生成する。`vosk` engine は optional dependency と model directory を明示して実行する local STT adapter で、repo に巨大依存や model を追加しない。`--dry-run --format json` は provider importability、model path、WAV 形式を preflight し、失敗時も fixture へ fallback しない。

URL / VOD を渡す CLI にはしない。URL 取得が必要な場合は、先に INT-02 `fetch-source-audio` または `fetch-source-video` でローカル素材を作り、必要なら `material_ledger` に登録してから `transcribe-audio` に渡す。

INT-02a の標準 source audio は `episodes/<episode_id>/materials/<material_id>/source.wav`（PCM WAV / mono / 16kHz / 16-bit）で、ledger entry は `kind="source_audio"` / `subkind="wav_pcm_16k_mono"` / `intended_uses=["editing_audio"]` を持つ。`transcribe-audio --material-id <id>` はこの ledger entry を確認し、`transcript.source_audio.material_id` に接続する。

### ED-09 review patch

`review-transcript` は v1 patch JSON を `transcript.json` に適用する。v1 で変更できるのは `segments[].text`、`segments[].review_status`、`segments[].notes`、および top-level `review.status` / `review.notes` / `review.reviewed_by` だけ。segment timing、source audio、STT provider/model/readback は変更しない。

```json
{
  "schema_version": "v1",
  "segments": [
    {
      "id": "seg_000001",
      "text": "corrected subtitle text",
      "review_status": "accepted",
      "notes": ["human corrected from Vosk output"]
    }
  ],
  "review": {
    "status": "needs_review",
    "notes": ["correction pass 1"]
  }
}
```

`review.status="approved"` にする場合は `--reviewed-by` または patch 内 `review.reviewed_by` が必須で、全 segment が `accepted` または `rejected` でなければ失敗する。`--dry-run --format json` は `updated_segment_count`、`review_status`、`segment_review_counts`、`schema_ok`、`dry_run` を返し、ファイルを書き換えない。

### ED-10 subtitle track import

`import-subtitle-track` imports an official/external subtitle track into a `transcript.json`-compatible artifact. v1 supports YouTube JSON3 only (`--source-format youtube-json3`). The base transcript anchors `episode_id`, `language`, and `source_audio`; subtitle events become new `segments[]`.

```bash
python -m src.cli.main import-subtitle-track \
  --base-transcript episodes/episode_example/transcript.json \
  --subtitle-track episodes/episode_example/source_subs/example.ja.json3 \
  --output episodes/episode_example/transcript.json \
  --reviewed-by user:operator \
  --dry-run \
  --format json
```

Imported transcripts use `stt.engine="subtitle_track"`, `stt.provider="youtube_subtitles"`, and `stt.engine_version="youtube-json3"`. `stt.params` records the subtitle track path, source format, base transcript engine/provider/segment count, and alignment overlap threshold. Segment notes record either `aligned_base_segment_id=... overlap_seconds=...` or `no_base_segment_overlap_above=...`.

The top-level review remains conservative (`needs_review`). Subtitle track import is a caption-completeness / alignment aid, not subtitle design, typography, safe-area, creative acceptance, rights approval, production render, or publishing acceptance. Downstream `generate-subtitles` marks these drafts as `source_type="imported_subtitle_track"`.

## Provider / model 採用状況

ED-10 adds `engine="subtitle_track"` for imported subtitle-track transcripts. The current provider is `youtube_subtitles` with YouTube JSON3 input under `episodes/<episode_id>/source_subs/*.json3`.

| Provider | engine value | language | 状態 | Model path 例 | Slice |
|---|---|---|---|---|---|
| fake fixture | `fake` | any | implemented | （CLI で `--fixture-segments` を渡す） | ED-07 |
| Vosk EN | `vosk` | `en` | implemented | `_tmp/stt_models/vosk-model-small-en-us-0.15` | ED-07b |
| Vosk JP | `vosk` | `ja` | implemented | `_tmp/stt_models/vosk-model-small-ja-0.22` | JP-STT-01 |
| whisper.cpp | `whisper-cpp` | any | proposed | — | future |
| OpenAI Whisper | `whisper` | any | proposed | — | future |

### Vosk JP smoke

operator runbook: [JP_STT_SMOKE.md](../../JP_STT_SMOKE.md)（model 入手 / 日本語 audio source 候補 / smoke 手順 / readback / トラブルシュート）

### Language ↔ Model 一貫性（ED-07c）

CLI は `--language` と `--model` の言語が一致しているかを、Vosk model path の basename から推定できる範囲で検証する。`--language` は `transcript.language` / `stt.params.language` の metadata readback として使われ、`--model` は実 STT 実行に使われるため、ここがズレると downstream の字幕・cut 評価が誤読される。

検証例:
- `--language en --model _tmp/stt_models/vosk-model-small-en-us-0.15` → `passed`
- `--language ja --model _tmp/stt_models/vosk-model-small-ja-0.22` → `passed`
- `--language ja --model _tmp/stt_models/vosk-model-small-en-us-0.15` → `failed`。CLI は `transcript.json` を書かない
- `--language ja --model _tmp/stt_models/model` → `not_inferable`。warning を `stt.warnings[]` に残し、operator が model と language の対応を確認する

`stt.params.language_model_check` は `passed` / `not_inferable` のいずれかを readback する。Vosk の推定言語は推定できた場合のみ `stt.params.model_language` に残す。dry-run では mismatch の `failed` も `language_model_check` に出るが、actual run では transcript を書かずに失敗する。
