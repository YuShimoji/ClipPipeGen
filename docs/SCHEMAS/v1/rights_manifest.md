# rights_manifest.schema (v1)

権利確認・公開可否ゲートの正本データ。1 episode に対して 1 manifest。Compliance / Rights レーンが書き、他レーンが gate として参照する。

## ファイル形式

JSON。配置は `episodes/<episode_id>/rights_manifest.json`。

## トップレベル構造

```json
{
  "schema_version": "v1",
  "episode_id": "ep_20260506_hololive_sample_001",
  "created_at": "2026-05-06T12:00:00+09:00",
  "updated_at": "2026-05-06T12:00:00+09:00",
  "source_video": { ... },
  "talents": [ ... ],
  "third_party_ip": [ ... ],
  "prohibited_assets": [ ... ],
  "required_disclosures": [ ... ],
  "publication_constraints": { ... },
  "compliance_check": { ... }
}
```

## フィールド定義

### `schema_version`（必須）

固定値 `"v1"`。互換性管理用。

### `episode_id`（必須）

文字列。`ep_<YYYYMMDD>_<source_label>_<seq>` 形式推奨。プロジェクト全体で一意。

### `source_video`（必須）

元動画の特定情報。

```json
{
  "url": "https://www.youtube.com/watch?v=XXXX",
  "platform": "youtube",
  "title": "動画タイトル",
  "channel": "チャンネル名",
  "channel_id": "UCxxxxxx",
  "vod_status": "public",
  "membership_only": false,
  "is_archived_live": true,
  "uploaded_at": "2026-04-01T20:00:00+09:00",
  "duration_seconds": 7200
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `url` | string | ✓ | 元動画 URL |
| `platform` | enum | ✓ | `youtube` / `twitch` 等。v1 は `youtube` のみサポート |
| `title` | string | ✓ | 元動画タイトル |
| `channel` | string | ✓ | チャンネル表示名 |
| `channel_id` | string | ✓ | プラットフォーム固有 ID |
| `vod_status` | enum | ✓ | `public` / `unlisted` / `private` / `members_only` / `deleted` |
| `membership_only` | boolean | ✓ | メンバー限定動画かどうか |
| `is_archived_live` | boolean | ✓ | ライブアーカイブかどうか（VTuber の二次創作ガイドラインで条件が違う場合がある） |
| `uploaded_at` | string (ISO 8601) | optional | 元動画投稿日時 |
| `duration_seconds` | number | optional | 元動画尺 |

### `talents`（必須、配列）

出演タレント情報。1人以上。

```json
[
  {
    "name": "タレント名",
    "agency": "hololive",
    "guideline_url": "https://www.hololive.tv/terms",
    "guideline_version_checked_at": "2026-05-06",
    "individual_policy_notes": []
  }
]
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `name` | string | ✓ | タレント表示名 |
| `agency` | enum | ✓ | `hololive` / `nijisanji` / `independent` 等。v1 は `hololive` 中心 |
| `guideline_url` | string | ✓ | 適用するガイドライン URL |
| `guideline_version_checked_at` | string (date) | ✓ | ガイドラインを参照した日 |
| `individual_policy_notes` | string[] | optional | タレント個別の追加方針（コメント・例外等） |

### `third_party_ip`（配列）

第三者 IP の混入情報。なければ空配列。

```json
[
  {
    "kind": "game",
    "name": "ゲームタイトル",
    "rights_holder": "発行元",
    "policy_url": "https://...",
    "permitted": true,
    "conditions": ["要出典明記", "収益化可"]
  }
]
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `kind` | enum | ✓ | `game` / `music` / `tv_show` / `movie` / `other` |
| `name` | string | ✓ | タイトル名 |
| `rights_holder` | string | ✓ | 権利者 |
| `policy_url` | string | optional | 公式ポリシー URL |
| `permitted` | boolean | ✓ | 二次利用可否（false なら `compliance_check.status` は `passed` にならない） |
| `conditions` | string[] | optional | 条件（出典明記・収益化可否等） |

### `prohibited_assets`（配列）

使用禁止素材。なければ空配列。

```json
[
  {
    "asset_kind": "music",
    "description": "BGM 'XXX'",
    "reason": "rights holder denies clip usage"
  }
]
```

### `required_disclosures`（配列）

概要欄等で必須の表記。

```json
[
  {
    "kind": "source_link",
    "text": "元動画: https://www.youtube.com/watch?v=XXXX"
  },
  {
    "kind": "rights_credit",
    "text": "© cover corp."
  }
]
```

| `kind` 候補 | 説明 |
|---|---|
| `source_link` | 元動画リンク |
| `rights_credit` | 権利者クレジット |
| `talent_credit` | タレントクレジット |
| `third_party_credit` | 第三者 IP クレジット |
| `custom` | カスタム表記 |

### `publication_constraints`

公開条件。

```json
{
  "earliest_publish_at": "2026-05-07T00:00:00+09:00",
  "monetization_allowed": true,
  "platforms_allowed": ["youtube"],
  "thumbnail_constraints": ["talent_face_required", "no_misleading_text"]
}
```

| フィールド | 説明 |
|---|---|
| `earliest_publish_at` | 元動画 VOD 化後の遅延等を考慮した最早公開可能時刻 |
| `monetization_allowed` | 収益化可否 |
| `platforms_allowed` | 公開可能プラットフォーム |
| `thumbnail_constraints` | サムネ制約（タレント顔必須・誤解を招く表記禁止等） |

### `compliance_check`（必須、gate 本体）

```json
{
  "status": "passed",
  "checked_at": "2026-05-06T12:30:00+09:00",
  "checked_by": "user:thankyoukass",
  "errors": [],
  "warnings": [],
  "gate_version": "v1"
}
```

| フィールド | 型 | 必須 | 説明 |
|---|---|---|---|
| `status` | enum | ✓ | `passed` / `pending` / `failed` |
| `checked_at` | string (ISO 8601) | ✓ if status != pending | 判定時刻 |
| `checked_by` | string | ✓ if status != pending | 判定者（人手判断が前提） |
| `errors` | object[] | ✓ | failed 理由（status=failed 時に必須） |
| `warnings` | object[] | ✓ | passed でも記録すべき注意点 |
| `gate_version` | string | ✓ | `compliance_check` ロジックのバージョン |

`errors[]` / `warnings[]` の項目構造:

```json
{
  "code": "VOD_NOT_PUBLIC",
  "field": "source_video.vod_status",
  "message": "元動画が public でない（現在: members_only）",
  "severity": "error"
}
```

## バリデーション規則

CR-01 validator が以下を強制する：

1. `schema_version == "v1"` 必須
2. `source_video.vod_status` が `private` / `members_only` / `deleted` の場合、`compliance_check.status` は `passed` にならない（自動 fail）
3. `talents[].agency == "hololive"` の場合、`talents[].guideline_url` がホロライブ公式ドメインを含むこと
4. `third_party_ip[].permitted == false` の項目が1つでもあれば `compliance_check.status` は `passed` にならない
5. `compliance_check.status == "passed"` には `checked_at` と `checked_by` が必須
6. `prohibited_assets[]` に登録された素材 ID が material_ledger に登録されていれば warning（fail にはしない、確認用）

## 後続バージョンの予定

- v2: `monetization_eligibility` の自動判定（ガイドラインバージョン管理）
- v2: `multi_source_video[]`（複数元動画からの切り抜き）
- v2: `talents[].character_use_constraints`（衣装・キャラ別制約）

v1 では上記は扱わない。
