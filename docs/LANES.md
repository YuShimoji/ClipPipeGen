# Lanes

4レーン＋Publishing の責務境界を明文化する。各レーンの inputs／outputs／隣接レーンとの境界が正本。

## 全体像

```
                    ┌─────────────────────┐
                    │ Compliance / Rights │ ← 記録・readback 層
                    │                     │
                    │   ┌──────────────┐  │
                    │   │  Publishing  │  │ ← rights readback を参照
                    │   └──────────────┘  │
                    └──────────┬──────────┘
                               │ 権利確認結果を要求／参照
                               ▼
                    ┌─────────────────────┐
                    │  Material Sourcing  │ ← 横断取得・台帳層
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
  src/integrations/asset_fetch/ ← Material Sourcing から呼ばれる
  future src/integrations/stt/  ← Editing から呼ばれる（engine wrapper。URL 取得は含めない）
  src/integrations/bg_removal/  ← Material Sourcing から呼ばれる（または外部処理結果を受領）
```

## 1. Compliance / Rights

### 責務

- 元動画 URL／VOD 公開状態／第三者 IP／利用条件／使用注意素材／概要欄表記の収集と記録
- ホロライブ二次創作ガイドライン・YouTube 規約・各タレント個別方針の落とし込み
- 他レーンへの `compliance_check.status` / warnings の readback
- Publishing に必要な metadata / disclosure 情報の提供

### Inputs

- ユーザー入力：元動画 URL、対象タレント、想定公開先
- Material Sourcing 経由で各素材の出典・利用条件 sidecar
- 外部参照（人手）：ガイドライン本文、規約文書

### Outputs

- `rights_manifest.json`（per-episode）
- `compliance_check.{status, errors, warnings, checked_at, review_version}`
- 概要欄必須表記テキスト（Publishing が利用）

### 境界

- **やる**：状態記録・ガイドライン項目の構造化・review notes の表示
- **やらない**：rights 値だけで他レーンの local CLI を停止する

## 2. Material Sourcing（横断レイヤー）

### 責務

- 動画素材／音声素材／サムネ素材／ロゴ／出典素材／人物画像／背景切り抜き結果を一元台帳化
- Editing／Thumbnail／Compliance からの素材要求の受付
- 外部 integration（asset_fetch / bg_removal）の呼び出し境界
- INT-02a では source audio の標準形（PCM WAV / mono / 16kHz / 16-bit）を `fetch-source-audio --mode fake` で生成し、ledger / sidecar / receipt に接続する

### Inputs

- 各レーンからの素材要求（種別・用途・必須条件）
- 外部処理結果（`src/integrations/asset_fetch/`、または人手で取得した素材＋sidecar）

### Outputs

- `material_ledger.json`（プロジェクト全体）
- `materials/<id>/<file>` ＋ `materials/<id>/sidecar.json`（出典・ライセンス・利用条件）

### 境界

- **やる**：台帳管理／sidecar 保持／integration 呼び出し境界の保持
- **やらない**：source/license/restriction の値だけで素材利用を停止する

## 3. Editing

### 責務

- ローカル音声ファイルからの transcript 生成（ED-07）
- `transcript.json` からのカット候補抽出
- 文脈チェック（カット境界が話者の発話を不自然に切断していないか）
- 字幕案の生成（テキスト＋タイミング、burned-in は外部）
- YMM4／外部 NLE への配置データ書き出し（cut EDL／字幕案／素材配置）

### Inputs

- `rights_manifest`（状態と review notes の参照）
- `material_ledger`（元動画素材・source audio material）
- `transcript.json`（ED-04 / ED-02 / ED-03 の入力。STT 実行後）
- ユーザー指示（切り抜きの主旨、希望尺、対象話題）

### Outputs

- `transcript.json`：STT segment と engine readback
- `edit_pack.json`：cut EDL、字幕案、配置プラン
- 外部 NLE 用 export（EDL／XML／CSV など、対象 NLE による）
- YMM4 用 base ymmp の slot patch input（必要な場合）

### 境界

- **やる**：ローカル音声からの transcript 生成、カット候補・文脈チェック・字幕案・配置データ
- **やらない**：実際のカット実行・concat・字幕焼き込み・動画レンダリング（YMM4／外部 NLE／人手）
- **分離する**：URL / VOD からの素材取得は INT-02 `asset_fetch`。`transcribe-audio` の内部に fetch を混ぜない
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
- **やらない**：現スライスではテンプレ authoring、文字＋立ち絵の自動合成、サムネ画像のレンダリングは未実装。必要になったら別 feature として起票
- **再利用**：NLMYTGen の `patch-thumbnail-template` / `audit-thumbnail-template` を CLI subprocess で呼ぶ

## 5. Publishing

### 責務

- YouTube metadata draft（タイトル・説明・タグ・category）
- upload / visibility 更新（`src/integrations/youtube/` 経由）
- thumbnail 設定（`thumbnails.set`）
- アップロード後の receipt 保存

### Inputs

- `rights_manifest`（status / warnings / disclosure 情報）
- 動画ファイル（YMM4／外部 NLE で書き出し済み、人手で配置）
- `thumbnail_patch` で生成したサムネ画像（YMM4 で書き出し済み）
- `edit_pack` の概要欄テキスト案＋Compliance の必須表記

### Outputs

- `publish_draft.json`：metadata 確定版
- `upload_receipt.json`：YouTube video ID、upload status、visibility 状態

### 境界

- **やる**：metadata 整形、upload、thumbnail 設定、visibility 更新、receipt 保存
- **やらない**：未実装の投稿後運用を docs だけで禁止扱いにする

## レーン間ハンドオフ

### Compliance → Editing / Thumbnail

- 渡すもの: `rights_manifest_id`、概要欄表記、使用注意素材リスト、第三者 IP notes
- 受け取り側 CLI は manifest を validate するが、`status != passed` だけでは早期失敗しない

### Material Sourcing → Editing / Thumbnail

- 渡すもの: `material_id`、素材ファイルパス、sidecar パス
- 受け取り側 CLI は sidecar の構造とファイル解決を確認する。source/license/restriction は readback として扱う
- Editing では source audio material（標準: `source.wav`, `subkind=wav_pcm_16k_mono`）を `transcribe-audio` に渡し、生成した `transcript.json` を ED-04 / ED-02 / ED-03 が参照する

### Editing / Thumbnail → Publishing

- 動画ファイル・サムネ画像は YMM4／外部 NLE／future renderer から渡す

### Publishing → 公開

- visibility 更新は future YouTube integration の一部として扱う。現時点では未実装。

## 関連ドキュメント

- 自動化境界の詳細：[AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- 各 schema：[SCHEMAS/v1/](SCHEMAS/v1/)
- 機能一覧：[FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
