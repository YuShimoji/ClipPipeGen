# thumbnail_patch_input.schema (v1)

YMM4 サムネテンプレへの slot patch を実行するための入力 schema。Thumbnail レーンの中心 artifact。NLMYTGen の `patch-thumbnail-template` CLI を subprocess で呼び出す際の bridge 入力でもある。

## ファイル形式

JSON。配置は `episodes/<episode_id>/thumbnail_patch_input.json`。

## 構造

```json
{
  "schema_version": "v1",
  "episode_id": "ep_20260506_hololive_sample_001",
  "rights_manifest_path": "episodes/ep_20260506_hololive_sample_001/rights_manifest.json",
  "material_ledger_path": "episodes/ep_20260506_hololive_sample_001/material_ledger.json",
  "base_template": {
    "ymmp_path": "templates/thumbnail/hololive_clip_v1.ymmp",
    "template_version": "v1",
    "audited_at": "2026-05-06T10:00:00+09:00"
  },
  "slots": [
    {
      "slot_id": "thumb.text.title",
      "kind": "text",
      "value": "ぺこら、まさかの大爆笑事件",
      "source_material_id": null
    },
    {
      "slot_id": "thumb.text.subtitle",
      "kind": "text",
      "value": "#ホロライブ切り抜き",
      "source_material_id": null
    },
    {
      "slot_id": "thumb.image.character",
      "kind": "image",
      "value": null,
      "source_material_id": "mat_001"
    },
    {
      "slot_id": "thumb.image.background",
      "kind": "image",
      "value": null,
      "source_material_id": "mat_002"
    }
  ],
  "output": {
    "ymmp_path": "episodes/ep_20260506_hololive_sample_001/thumbnail_patched.ymmp",
    "overwrite_existing": false
  }
}
```

## フィールド定義

### `schema_version`（必須）

固定値 `"v1"`。

### `episode_id`（必須）

紐付く episode。

### `rights_manifest_path`（必須）

`rights_manifest.json` への相対パス。CLI runner が読み込み、`compliance_check.status` を readback に残す。値だけでは hard gate にしない。

### `material_ledger_path`（必須）

`material_ledger.json` への相対パス。`source_material_id` の解決と sidecar 検証に使う。

### `base_template`（必須）

```json
{
  "ymmp_path": "templates/thumbnail/hololive_clip_v1.ymmp",
  "template_version": "v1",
  "audited_at": "ISO 8601"
}
```

| フィールド | 説明 |
|---|---|
| `ymmp_path` | YMM4 で人手 authoring 済みの base template ymmp（slot に `Remark=thumb.*.<id>` が設定されている前提） |
| `template_version` | テンプレ作成側のバージョン管理 |
| `audited_at` | NLMYTGen の `audit-thumbnail-template` で slot 健全性を確認した時刻 |

### `slots[]`（必須、空配列禁止）

```json
{
  "slot_id": "thumb.text.title",
  "kind": "text" | "image" | "color" | "transform",
  "value": "...",
  "source_material_id": "mat_001" | null
}
```

| フィールド | 必須 | 説明 |
|---|---|---|
| `slot_id` | ✓ | base template 内の `Remark` 値と一致。`thumb.text.<id>` または `thumb.image.<id>` または `thumb.color.<id>` または `thumb.transform.<id>` |
| `kind` | ✓ | `text` / `image` / `color` / `transform` |
| `value` | ✓ if `kind in (text, color, transform)` | テキスト本文 / 色 / transform 値 |
| `source_material_id` | ✓ if `kind == image` | `material_ledger.materials[].id` |

### `output`（必須）

```json
{
  "ymmp_path": "episodes/.../thumbnail_patched.ymmp",
  "overwrite_existing": false
}
```

`overwrite_existing == false` で既存ファイルあり → CLI 失敗。理由: 元ファイル保持。

## CLI 呼び出しフロー

```
+--------------------------+
| thumbnail_patch_input    |
+------------+-------------+
             |
             v
+--------------------------+
| ClipPipeGen CLI:         |
|   patch-thumbnail        |
+------------+-------------+
             |
             |  (1) rights manifest readback
             |      rights_manifest.compliance_check.status を記録
             |  (2) material_ledger validate
             |      ・source_material_id 解決
             |      ・sidecar schema / file path 解決
             |      ・source/license/restriction は metadata として保持
             |  (3) NLMYTGen subprocess:
             |      audit-thumbnail-template <base_template.ymmp_path>
             |      （slot の存在確認）
             |  (4) NLMYTGen subprocess:
             |      patch-thumbnail-template
             |        --input <base_template.ymmp_path>
             |        --output <output.ymmp_path>
             |        --slot-text  thumb.text.title  "..."
             |        --slot-image thumb.image.character "<resolved file path>"
             |        ...
             |  (5) readback parse
             |      patched ymmp の slot 値が input と一致するか
             v
+--------------------------+
| thumbnail_patch_result   |
+--------------------------+
```

## thumbnail_patch_result（出力）

CLI 実行結果。`episodes/<episode_id>/thumbnail_patch_result.json` に書き出す。

```json
{
  "schema_version": "v1",
  "input_path": "episodes/.../thumbnail_patch_input.json",
  "executed_at": "2026-05-06T13:00:00+09:00",
  "rights_readback": {
    "status": "read",
    "rights_manifest_status": "passed"
  },
  "material_validation": {
    "all_resolved": true,
    "violations": []
  },
  "audit_result": {
    "passed": true,
    "missing_slots": [],
    "extra_slots": []
  },
  "patch_result": {
    "output_ymmp_path": "episodes/.../thumbnail_patched.ymmp",
    "applied_slots": [
      {
        "slot_id": "thumb.text.title",
        "applied_value": "ぺこら、まさかの大爆笑事件",
        "readback_match": true
      },
      {
        "slot_id": "thumb.image.character",
        "applied_path": "materials/mat_001/character_pekora_transparent.png",
        "readback_match": true
      }
    ],
    "errors": []
  }
}
```

## バリデーション規則

TH-01 validator / CLI が以下を強制する：

1. `slots[]` が空配列でない
2. `slot_id` 形式が `thumb\.(text|image|color|transform)\.[a-z0-9_]+` に合致
3. `kind == "image"` の slot は `source_material_id` 必須、material_ledger に存在
4. 解決した素材の sidecar が schema として valid
5. `compliance_check.status` は rights_manifest 側から readback するが、値だけでは fail しない
6. `audit-thumbnail-template` が pass する（slot が base template に存在する）
7. `output.overwrite_existing == false` で既存ファイルがあれば fail

## 後続バージョンの予定

- v2: variation history（同 episode で複数サムネ案を比較する）
- v2: A/B candidate 生成（`thumb.text.title` の複数案）

v1 では1 episode 1サムネのみ。
