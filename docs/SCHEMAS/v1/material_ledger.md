# material_ledger.schema (v1)

素材の横断台帳。Editing／Thumbnail／Compliance 全てがこれを参照する。

## ファイル形式

JSON。配置は `episodes/<episode_id>/material_ledger.json`、または project-wide なら `materials/ledger.json`。Slice 1 では episode 単位。

## トップレベル構造

```json
{
  "schema_version": "v1",
  "episode_id": "ep_20260506_hololive_sample_001",
  "created_at": "2026-05-06T12:00:00+09:00",
  "updated_at": "2026-05-06T12:00:00+09:00",
  "materials": [ ... ]
}
```

## materials[] の構造

```json
{
  "id": "mat_001",
  "kind": "character_image",
  "subkind": "transparent_png",
  "file_path": "materials/mat_001/character_pekora_transparent.png",
  "sidecar_path": "materials/mat_001/sidecar.json",
  "hash_sha256": "abcdef0123...",
  "byte_size": 1234567,
  "intended_uses": ["thumbnail"],
  "registered_at": "2026-05-06T12:00:00+09:00",
  "registered_by": "user:thankyoukass",
  "compliance_link": {
    "rights_manifest_id": "ep_20260506_hololive_sample_001",
    "compliance_status_at_registration": "pending"
  }
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `id` | string | ✓ | episode 内で一意。`mat_<seq>` 形式推奨 |
| `kind` | enum | ✓ | 下記参照 |
| `subkind` | string | optional | kind 内の細分（例: `character_image` の `transparent_png` / `opaque_jpg`） |
| `file_path` | string | ✓ | リポルートからの相対パス |
| `sidecar_path` | string | ✓ | `material_sidecar.schema` に従う sidecar ファイル |
| `hash_sha256` | string | ✓ | ファイル整合性用 |
| `byte_size` | number | ✓ | バイトサイズ |
| `intended_uses` | enum[] | ✓ | 下記参照。空配列禁止 |
| `registered_at` | string (ISO 8601) | ✓ | 登録時刻 |
| `registered_by` | string | ✓ | 登録者 |
| `compliance_link` | object | ✓ | Compliance との紐付け |

### `kind` 候補

| 値 | 説明 |
|---|---|
| `source_video` | 元動画ファイル（ダウンロード後ローカル） |
| `source_audio` | 元音声（cut/抽出した結果含む） |
| `character_image` | タレント／キャラクター画像 |
| `background_image` | 背景画像 |
| `logo` | ロゴ・チャンネルアート |
| `font_asset` | フォントファイル |
| `bgm` | BGM 素材 |
| `se` | 効果音 |
| `attribution_text` | 出典テキスト素材 |
| `other` | その他（subkind で詳細） |

### `intended_uses` 候補

| 値 | 説明 |
|---|---|
| `thumbnail` | サムネ用 |
| `editing_overlay` | 動画編集中のオーバーレイ |
| `editing_bg` | 動画編集中の背景 |
| `editing_audio` | 動画編集中の音声 |
| `description_text` | 概要欄テキスト |
| `reference_only` | 参考のみ（最終出力に含めない） |

### `compliance_link`

```json
{
  "rights_manifest_id": "ep_20260506_hololive_sample_001",
  "compliance_status_at_registration": "pending"
}
```

| フィールド | 説明 |
|---|---|
| `rights_manifest_id` | この素材が紐付く `rights_manifest.episode_id` |
| `compliance_status_at_registration` | 登録時の `compliance_check.status` snapshot。実行時は manifest 側を再 read する |

## バリデーション規則

MS-01 validator が以下を強制する：

1. `materials[].id` は episode 内で一意
2. `file_path` 先のファイルが実在し、`hash_sha256` と一致
3. `sidecar_path` 先のファイルが実在し、material_sidecar.schema を満たす
4. `intended_uses` が空配列でない
5. `compliance_link.rights_manifest_id` が同 episode の rights_manifest と一致
6. `kind == "character_image"` で `subkind == "transparent_png"` の場合、ファイル形式が PNG かつアルファチャンネルを持つ（PNG header + IHDR チェック、外部依存なし）

## CLI 操作

| コマンド | 操作 |
|---|---|
| `register-material` | 素材を ledger に追加（sidecar 必須） |
| `list-materials` | ledger を表示（filter: kind / intended_uses） |
| `audit-material-ledger` | 整合性チェック（hash・sidecar・compliance_link）。NLMYTGen の `audit-*` 命名規則に揃える |
| `remove-material` | 物理削除はせず ledger entry を `archived` フラグで残す |

## 後続バージョンの予定

- v2: `derived_from`（背景切り抜き元の original 画像との紐付け）
- v2: project-wide ledger と episode-wide ledger の統合

v1 では episode 単位のみ。
