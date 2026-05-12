# edit_pack.schema (v1)

Editing レーンの中心 artifact。元動画からの cut 候補、選択 cut、字幕案、文脈チェック状態を 1 episode 単位で保持する。ED-01 では **schema / validator / skeleton CLI** を確定し、ED-02 / ED-03 / ED-04 / ED-06 が同じ `edit_pack` を cut generation、context check、subtitle draft、外部 NLE 向け export へ接続する。STT の出力は [transcript.schema](transcript.md) として分離し、`edit_pack` は transcript から生成・転記された cut / subtitle / review を保持する。

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
    "notes": [],
    "checked_at": null,
    "source": null
  },
  "source_segment_ids": ["seg_000001", "seg_000002"]
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
| `context_check.checked_at` | string/null | optional | ED-03 `check-cut-context` の実行時刻 |
| `context_check.source` | string/null | optional | 文脈チェック実装の readback。現行は `transcript_boundary_v1` |
| `source_segment_ids` | string[] | optional | `transcript.segments[]` 由来なら元 segment ID 群。ED-02 が付与する |

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
  "style_slot": "subtitle.default",
  "source_segment_id": "seg_000001"
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
| `source_segment_id` | string | optional | `transcript.segments[].id` 由来ならその ID。ED-04 が付与する |

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
- `transcribe-audio` は ED-07 の責務であり、既存のローカル音声ファイルから `transcript.json` を生成する。URL / VOD 取得は INT-02 `asset_fetch` の責務。
- ED-01 は Editing レーンの **器** を確定するだけ。外部 API と元動画ダウンロードは発生しない。

## CLI（ED-01 / ED-02a / ED-02 / ED-03 / ED-04 / ED-06）

```bash
python -m src.cli.main init-edit-pack --episode-id ep_x
python -m src.cli.main validate-edit-pack --edit-pack episodes/ep_x/edit_pack.json
python -m src.cli.main add-cut-candidate \
  --edit-pack episodes/ep_x/edit_pack.json \
  --start-seconds 120.0 \
  --end-seconds 185.0 \
  --reason "manual highlight" \
  --select

python -m src.cli.main generate-cuts \
  --transcript episodes/ep_x/transcript.json \
  --edit-pack episodes/ep_x/edit_pack.json \
  --target-duration-seconds 60 \
  --select-generated

python -m src.cli.main check-cut-context \
  --transcript episodes/ep_x/transcript.json \
  --edit-pack episodes/ep_x/edit_pack.json \
  --selected-cuts-only

python -m src.cli.main generate-subtitles \
  --transcript episodes/ep_x/transcript.json \
  --edit-pack episodes/ep_x/edit_pack.json \
  --wrap-eaw 28

python -m src.cli.main export-nle \
  --edit-pack episodes/ep_x/edit_pack.json \
  --preview-manifest episodes/ep_x/preview_manifest.json \
  --output-dir episodes/ep_x/exports/ed06
```

`add-cut-candidate` は ED-02a の手動/インポート入力スライス。元動画解析・speech-to-text・自動検出は行わず、人手または別ツールで得た秒数を `edit_pack` に記録するだけ。後続の ED-02 / ED-04 は `transcript.json` を読んで同じ `edit_pack` に candidate / subtitle を追加する。

`generate-cuts` は ED-02 の自動 cut 候補生成スライス。`transcript.json` の segment timing / text density / topic hint を使って `edit_pack.cut_candidates[]` を追加する。文脈妥当性の判定はせず、`context_check.status="not_checked"` として ED-03 に渡す。

`check-cut-context` は ED-03 の文脈チェック。`transcript.json` の隣接 segment を見て、cut 境界が発話途中を切っていないか、`source_segment_ids` が transcript と対応しているか、近接する前後発話があるかを `context_check.status` と notes に記録する。動画 preview / NLE export / creative acceptance は行わない。

`generate-subtitles` は ED-04 の subtitle draft 生成スライス。`transcript.json` の `segments[]` を `edit_pack.subtitles[]` に変換し、`--wrap-eaw` 指定時は ED-05 の EAW 折返しを使って `text` に改行を入れる。実 STT、URL/VOD 取得、動画レンダリング、字幕焼き込みは行わない。

`export-nle` は ED-06 の最小 NLE handoff。`edit_pack.cut_candidates[]` / `selected_cut_ids[]` / `subtitles[]` と、可能な範囲の source audio provenance を `nle_cut_list.csv`、`nle_export_manifest.json`、`nle_export_report.html` に出力する。これは外部編集ソフトへ渡すための plumbing proof であり、FCPXML / Resolve XML、render / encode、production edit acceptance は行わない。詳細は [nle_export.md](nle_export.md)。
