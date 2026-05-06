# Lanes

4レーン＋1 sub-gate の責務境界を明文化する。各レーンの inputs／outputs／隣接レーンとの境界が正本。

## 全体像

```
                    ┌─────────────────────┐
                    │ Compliance / Rights │ ← 決定層（gate keeper）
                    │                     │
                    │   ┌──────────────┐  │
                    │   │  Publishing  │  │ ← Compliance.gate=PASS が必要
                    │   └──────────────┘  │
                    └──────────┬──────────┘
                               │ 権利確認結果を要求／参照
                               ▼
                    ┌─────────────────────┐
                    │  Material Sourcing  │ ← 横断取得層
                    └──────────┬──────────┘
                       要求    │    供給
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
         ┌─────────┐      ┌─────────┐      ┌─────────┐
         │ Editing │      │Thumbnail│      │Compliance│ ← 出典・利用条件確認
         └─────────┘      └─────────┘      │（再循環）│
                                            └─────────┘

外部境界（隔離）:
  src/integrations/youtube/   ← Publishing から呼ばれる
  src/integrations/asset_fetch/ ← Material Sourcing から呼ばれる（Compliance ゲート後）
  src/integrations/bg_removal/  ← Material Sourcing から呼ばれる（または外部処理結果を受領）
```

## 1. Compliance / Rights

### 責務

- 元動画 URL／VOD 公開状態／第三者 IP／利用条件／使用禁止素材／概要欄必須表記の収集と判定
- ホロライブ二次創作ガイドライン・YouTube 規約・各タレント個別方針の落とし込み
- 公開可否ゲートの提供（他レーンへの `compliance_check.status` 出力）
- Publishing への最終 gate

### Inputs

- ユーザー入力：元動画 URL、対象タレント、想定公開先
- Material Sourcing 経由で各素材の出典・利用条件 sidecar
- 外部参照（人手）：ガイドライン本文、規約文書

### Outputs

- `rights_manifest.json`（per-episode）
- `compliance_check.{status, errors, checked_at, gate_version}`
- 概要欄必須表記テキスト（Publishing が利用）

### 境界

- **やる**：判定・ゲート提供・ガイドライン項目の構造化
- **やらない**：自動取得（取得は Material Sourcing 経由）／自動投稿・公開（Publishing は private/unlisted まで、公開は人手）

## 2. Material Sourcing（横断レイヤー）

### 責務

- 動画素材／サムネ素材／ロゴ／出典素材／人物画像／背景切り抜き結果を一元台帳化
- Editing／Thumbnail／Compliance からの素材要求の受付
- 外部 integration（asset_fetch / bg_removal）の呼び出し境界

### Inputs

- 各レーンからの素材要求（種別・用途・必須条件）
- 外部処理結果（`src/integrations/asset_fetch/` または人手で取得した素材＋sidecar）

### Outputs

- `material_ledger.json`（プロジェクト全体）
- `materials/<id>/<file>` ＋ `materials/<id>/sidecar.json`（出典・ライセンス・利用条件）

### 境界

- **やる**：台帳管理／sidecar 強制／integration 呼び出し境界の保持
- **やらない**：素材の自動加工（背景切り抜きは integration 結果を受領するのみ）／用途判断（用途は要求元レーンが決める）

## 3. Editing

### 責務

- 元動画からのカット候補抽出
- 文脈チェック（カット境界が話者の発話を不自然に切断していないか）
- 字幕案の生成（テキスト＋タイミング、burned-in は外部）
- YMM4／外部 NLE への配置データ書き出し（cut EDL／字幕案／素材配置）

### Inputs

- `rights_manifest`（compliance gate 通過確認）
- `material_ledger`（元動画素材）
- ユーザー指示（切り抜きの主旨、希望尺、対象話題）

### Outputs

- `edit_pack.json`：cut EDL、字幕案、配置プラン
- 外部 NLE 用 export（EDL／XML／CSV など、対象 NLE による）
- YMM4 用 base ymmp の slot patch input（必要な場合）

### 境界

- **やる**：カット候補・文脈チェック・字幕案・配置データ
- **やらない**：実際のカット実行・concat・字幕焼き込み・動画レンダリング（YMM4／外部 NLE／人手）
- **NLMYTGen 共通化しない**：NLMYTGen の S-3 CSV／S-6 Production IR／skit_group は構造が違うので使わない。共通化候補は字幕表示幅計測のみ。

## 4. Thumbnail

### 責務

- YMM4 サムネテンプレへの `thumb.image.*` / `thumb.text.*` slot patch 適用
- 透過PNG（人物画像）の受け入れと slot 配置
- patch 結果の readback（どの素材がどの slot に入ったか）

### Inputs

- `material_ledger` の人物画像（透過PNG）／背景／ロゴ
- ユーザー入力：テキスト案、対象テンプレ
- YMM4 サムネ base template `.ymmp`（人手で authoring 済み）

### Outputs

- patched `.ymmp`（YMM4 で開いて最終確認・調整・書き出し）
- `thumbnail_patch.json`：どの material_id がどの slot に入ったか

### 境界

- **やる**：slot patch、透過PNG 受け入れ、readback
- **やらない**：テンプレ authoring（人手 in YMM4）、文字＋立ち絵の自動合成、構図・配色・最終クリック感の自動決定、サムネ画像のレンダリング（YMM4 で書き出し）
- **再利用**：NLMYTGen の `patch-thumbnail-template` / `audit-thumbnail-template` を CLI subprocess で呼ぶ

## 5. Publishing（Compliance 内 gate）

### 責務

- YouTube metadata draft（タイトル・説明・タグ・category）
- private／unlisted upload（`src/integrations/youtube/` 経由）
- thumbnail 設定（`thumbnails.set`）
- アップロード後の receipt 保存

### Inputs

- `rights_manifest.compliance_check.status == "passed"`（必須）
- 動画ファイル（YMM4／外部 NLE で書き出し済み、人手で配置）
- `thumbnail_patch` で生成したサムネ画像（YMM4 で書き出し済み）
- `edit_pack` の概要欄テキスト案＋Compliance の必須表記

### Outputs

- `publish_draft.json`：metadata 確定版
- `upload_receipt.json`：YouTube video ID、upload status、private/unlisted 状態
- **公開は人手で YouTube Studio から実行**

### 境界

- **やる**：metadata 整形、private/unlisted upload、thumbnail 設定、receipt 保存
- **やらない**：公開（`status: public` への切替）、自動公開スケジューリング、コメント／タグ自動応答、収益化設定の自動切替

## レーン間ハンドオフ

### Compliance → Editing / Thumbnail

- gate: `rights_manifest.compliance_check.status == "passed"`
- 渡すもの: `rights_manifest_id`、概要欄必須表記、使用禁止素材リスト、第三者 IP 配慮事項
- 受け取り側 CLI は manifest を validate し、`status != passed` なら早期失敗

### Material Sourcing → Editing / Thumbnail

- 渡すもの: `material_id`、素材ファイルパス、sidecar パス
- 受け取り側 CLI は sidecar の利用条件を読み、用途と整合するか確認（例：「サムネ不可」素材が thumbnail に渡されたら失敗）

### Editing / Thumbnail → Publishing

- 動画ファイル・サムネ画像は人手で YMM4／外部 NLE から書き出し、ファイルパスを CLI に渡す
- Python は動画ファイルそのものを生成しない

### Publishing → 公開

- 公開は YouTube Studio で人手実行。Python は upload までで止まる。

## 関連ドキュメント

- 自動化境界の詳細：[AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- 各 schema：[SCHEMAS/v1/](SCHEMAS/v1/)
- 機能一覧：[FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
