# edit_pack.schema (v1)

Editing レーンの中心 artifact。元動画からの cut 候補、選択 cut、字幕案、文脈チェック状態を 1 episode 単位で保持する。ED-01 では **schema / validator / skeleton CLI** までを扱い、cut detection・字幕生成・NLE export は後続 ED-02 以降に残す。

## ファイル形式

JSON。配置は `episodes/<episode_id>/edit_pack.json`。

## トップレベル構造

```json
{
  "schema_version": "v1",
  "episode_id": "ep_20260506_hololive_sample_001",
  "rights_manifest_path": "episodes/ep_20260506_hololive_sample_001/rights_manifest.json",
  "material_ledger_path": "episodes/ep_20260506_hololive_sample_001/material_ledger.json",
  "created_at": "2026-05-07T12:00:00+09:00",
  "updated_at": "2026-05-07T12:00:00+09:00",
  "editing_intent": {
    "target_duration_seconds": 60,
    "topic": "",
    "audience_note": "",
    "language": "ja"
  },
  "cut_candidates": [],
  "selected_cut_ids": [],
  "subtitles": [],
  "review": {
    "status": "draft",
    "reviewed_by": null,
    "reviewed_at": null,
    "notes": []
  }
}
```

## フィールド定義

### `editing_intent`

切り抜きの狙いを記録する。自動検出の入力条件にもなるが、ED-01 では文字列と数値の保持のみ。

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `target_duration_seconds` | number | optional | 目標尺 |
| `topic` | string | optional | 切り抜きたい話題 |
| `audience_note` | string | optional | 視聴者・投稿意図のメモ |
| `language` | string | ✓ | `ja` / `en` 等 |

### `cut_candidates[]`

```json
{
  "id": "cut_001",
  "start_seconds": 123.45,
  "end_seconds": 184.20,
  "source": "manual",
  "reason": "Main punchline starts here",
  "confidence": 1.0,
  "context_check": {
    "status": "not_checked",
    "notes": []
  }
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✓ | episode 内で一意。`cut_<seq>` 推奨 |
| `start_seconds` | number | ✓ | 元動画上の開始秒 |
| `end_seconds` | number | ✓ | 元動画上の終了秒。`start_seconds < end_seconds` 必須 |
| `source` | enum | ✓ | `manual` / `auto` / `imported` |
| `reason` | string | optional | 候補理由 |
| `confidence` | number | optional | 0.0〜1.0。manual は 1.0 推奨 |
| `context_check.status` | enum | ✓ | `not_checked` / `passed` / `needs_review` / `failed` |
| `context_check.notes` | string[] | optional | 文脈上の懸念や判断メモ |

### `selected_cut_ids[]`

最終的に採用する cut の ID 配列。`cut_candidates[].id` に存在しない ID は schema violation。

### `subtitles[]`

```json
{
  "id": "sub_001",
  "cut_id": "cut_001",
  "start_seconds": 123.45,
  "end_seconds": 126.00,
  "text": "ここが一番おもしろいところ",
  "source": "manual",
  "style_slot": "subtitle.default"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✓ | episode 内で一意 |
| `cut_id` | string | optional | 紐付く `cut_candidates[].id` |
| `start_seconds` | number | ✓ | 元動画上の字幕開始秒 |
| `end_seconds` | number | ✓ | 元動画上の字幕終了秒 |
| `text` | string | ✓ | 字幕本文。空文字禁止 |
| `source` | enum | ✓ | `manual` / `auto` / `imported` |
| `style_slot` | string | optional | 後段 YMM4/NLE 用の表示スタイル名 |

### `review`

```json
{
  "status": "draft",
  "reviewed_by": null,
  "reviewed_at": null,
  "notes": []
}
```

`status` 候補: `draft` / `needs_review` / `approved` / `rejected`

`status == "approved"` の場合、`reviewed_by` と `reviewed_at` が必須。

## バリデーション規則

ED-01 validator が以下を強制する：

1. `schema_version == "v1"`
2. `episode_id` / `rights_manifest_path` / `created_at` / `updated_at` 必須
3. `editing_intent.language` 必須
4. `cut_candidates[].id` は一意
5. `cut_candidates[].start_seconds < end_seconds`
6. `cut_candidates[].source in {"manual","auto","imported"}`
7. `context_check.status in {"not_checked","passed","needs_review","failed"}`
8. `selected_cut_ids[]` はすべて `cut_candidates[].id` に存在
9. `subtitles[].id` は一意
10. `subtitles[].start_seconds < end_seconds`
11. `subtitles[].text` は空文字禁止
12. `subtitles[].cut_id` がある場合は `cut_candidates[].id` に存在
13. `review.status == "approved"` の場合、`reviewed_by` / `reviewed_at` 必須

## 境界

- ED-01 では動画ファイルを作らない。
- ED-01 では cut detection / speech-to-text / subtitle generation を呼ばない。
- ED-01 は Editing レーンの **器** を確定するだけ。外部 API と元動画ダウンロードは発生しない。

## CLI（ED-01 / ED-02a）

```bash
python -m src.cli.main init-edit-pack --episode-id ep_x
python -m src.cli.main validate-edit-pack --edit-pack episodes/ep_x/edit_pack.json
python -m src.cli.main add-cut-candidate \
  --edit-pack episodes/ep_x/edit_pack.json \
  --start-seconds 120.0 \
  --end-seconds 185.0 \
  --reason "manual highlight" \
  --select
```

`add-cut-candidate` は ED-02a の安全スライス。元動画解析・speech-to-text・自動検出は行わず、人手または別ツールで得た秒数を `edit_pack` に記録するだけ。
