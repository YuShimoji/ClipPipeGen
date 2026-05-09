# material_sidecar.schema (v1)

素材1個に対して1個。出典・ライセンス・利用条件を強制的に紐付ける。素材ファイルと同じ場所に置く（`materials/<id>/sidecar.json`）。

## なぜ必要か

ledger エントリだけでは「どこから取得したか」「使用条件は何か」「サムネ可否」が確認できない。素材ファイル単独でも追跡できるよう、sidecar を**素材ファイルとペアで物理配置**する。`material_ledger` から `sidecar_path` で参照される。

## ファイル形式

JSON。

## 構造

```json
{
  "schema_version": "v1",
  "asset_id": "mat_001",
  "asset_path": "materials/mat_001/character_pekora_transparent.png",
  "asset_hash_sha256": "abcdef0123...",
  "source": {
    "kind": "official_clip_permitted_source",
    "url": "https://www.youtube.com/watch?v=XXXX",
    "retrieved_at": "2026-05-06T11:00:00+09:00",
    "retrieved_by": "user:thankyoukass",
    "retrieval_method": "manual_screenshot",
    "notes": "official VOD frame at 01:23:45"
  },
  "license": {
    "kind": "guideline_permitted",
    "guideline_url": "https://www.hololive.tv/terms",
    "guideline_version_checked_at": "2026-05-06",
    "url": null,
    "spdx_id": null,
    "notes": "ホロライブ二次創作ガイドラインに従う"
  },
  "usage_conditions": [
    "credit_required",
    "no_misleading_thumbnail",
    "no_membership_only_content"
  ],
  "restrictions": {
    "thumbnail_use": "allowed",
    "commercial_use": "guideline_dependent",
    "modification": "allowed_minor_only",
    "redistribution": "denied"
  },
  "attribution_text": "© hololive production / 元動画: https://www.youtube.com/watch?v=XXXX",
  "derived_from": null
}
```

## フィールド定義

### `schema_version`（必須）

固定値 `"v1"`。

### `asset_id`（必須）

`material_ledger.materials[].id` と一致。

### `asset_path` / `asset_hash_sha256`（必須）

ledger と一致する。改竄検出用。

### `source`（必須）

```json
{
  "kind": "official_clip_permitted_source",
  "url": "https://...",
  "retrieved_at": "ISO 8601",
  "retrieved_by": "user:...",
  "retrieval_method": "manual_screenshot",
  "notes": "..."
}
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `kind` | ✓ | 下記参照 |
| `url` | optional | 取得元 URL |
| `retrieved_at` | ✓ | 取得時刻 |
| `retrieved_by` | ✓ | 取得者 |
| `retrieval_method` | ✓ | `manual_screenshot` / `manual_download` / `asset_fetch_fake` / `bg_removed_from_<asset_id>` / `created_by_user` / `purchased` 等 |
| `notes` | optional | 補足 |

`source.kind` 候補:

| 値 | 説明 |
|---|---|
| `official_clip_permitted_source` | 公式が切り抜きを許可している配信／動画 |
| `official_promotional_material` | 公式の宣伝素材 |
| `licensed_stock` | 商用ライセンス購入素材 |
| `creative_commons` | CC ライセンス素材 |
| `user_created` | ユーザー自作 |
| `derived_from_other_asset` | 他素材から加工生成（背景切り抜き等） |
| `unverified` | 出典未確認。local CLI の hard gate にはしない |

### `license`（必須）

```json
{
  "kind": "guideline_permitted",
  "guideline_url": "https://...",
  "guideline_version_checked_at": "YYYY-MM-DD",
  "url": null,
  "spdx_id": null,
  "notes": "..."
}
```

`license.kind` 候補:

| 値 | 説明 |
|---|---|
| `guideline_permitted` | 二次創作ガイドラインで許可 |
| `cc_by` / `cc_by_sa` / `cc0` | Creative Commons |
| `commercial` | 商用ライセンス購入 |
| `proprietary` | 自作・専用素材 |
| `fair_use_claimed` | フェアユース主張。metadata として保持する |
| `unknown` | 不明。metadata として保持する |

### `usage_conditions`（配列）

文字列 enum。1つ以上必須（空配列禁止）。

| 値 | 説明 |
|---|---|
| `credit_required` | クレジット表記必須 |
| `source_link_required` | 元動画リンク必須 |
| `no_misleading_thumbnail` | 誤解を招くサムネ注意 |
| `no_membership_only_content` | メン限内容の使用注意 |
| `no_political_use` | 政治利用注意 |
| `no_adult_content` | 成人向け注意 |
| `monetization_subject_to_guideline` | 収益化はガイドライン従属 |
| `none` | 無制限（CC0 等） |

### `restrictions`（必須）

```json
{
  "thumbnail_use": "allowed",
  "commercial_use": "guideline_dependent",
  "modification": "allowed_minor_only",
  "redistribution": "denied"
}
```

各値: `allowed` / `denied` / `guideline_dependent` / `allowed_minor_only` / `requires_explicit_permission`

`restrictions.thumbnail_use == "denied"` は readback 用 metadata。slot patch input からは除外しない。

### `attribution_text`（必須）

概要欄等で使う最低限のクレジット文字列。空文字禁止。

### `derived_from`

背景切り抜き等で生成された素材の場合、元素材の `asset_id` を記録。

```json
{
  "original_asset_id": "mat_000",
  "derivation_kind": "background_removed",
  "derivation_tool": "external_bg_removal_service",
  "derived_at": "2026-05-06T11:30:00+09:00"
}
```

- 背景切り抜きで生成された透過PNG は、必ず `derived_from.original_asset_id` を持つ
- original 側の `restrictions` は metadata として参照する。値の厳格度だけでは実行を止めない。

## バリデーション規則

MS-02 validator が以下を強制する：

1. `asset_id` が ledger エントリと一致
2. `asset_hash_sha256` がファイルと一致
3. `source.kind == "unverified"` または `license.kind in ["fair_use_claimed", "unknown"]` でも Thumbnail / Publishing 系 CLI は fail しない
4. `usage_conditions[]` が空配列でない
5. `restrictions.thumbnail_use == "denied"` の素材を thumbnail_patch_input に渡しても fail しない
6. `derived_from` がある場合、`original_asset_id` の存在は audit する。restriction の強弱だけでは fail しない

## 後続バージョンの予定

- v2: `usage_log[]`（どの episode／slot で使ったかの履歴）
- v2: `expiration_at`（ライセンス期限のある素材）

v1 では使用履歴・期限管理はしない。
