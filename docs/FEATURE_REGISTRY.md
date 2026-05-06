# Feature Registry

全機能を ID で管理する。登録されていない機能は追加しない。`proposed` はユーザー承認後に `approved` へ昇格してから実装する。

## ID 規則

| プレフィックス | レーン |
|---|---|
| CR-* | Compliance / Rights |
| MS-* | Material Sourcing |
| ED-* | Editing |
| TH-* | Thumbnail |
| PB-* | Publishing |
| INT-* | Integrations（外部 API・AI サービス境界） |
| SH-* | Shared infra（CLI runner・schema validator・config） |

NLMYTGen 側の FEATURE ID（A-* / B-* 等）とは独立。

## 状態

- `proposed` — 提案中。実装着手不可。
- `approved` — ユーザー承認済み。実装着手可。
- `in_progress` — 実装中。
- `done` — 実装＋acceptance 完了。
- `hold` — 一時停止。再開条件を明記する。
- `rejected` — 廃止。理由を残す。

## Slice 1 スコープ（最初の実証）

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| **CR-01** | rights_manifest schema v1 と validator | approved | `docs/SCHEMAS/v1/rights_manifest.md` の構造を実装。`compliance_check.status` を CLI gate として強制 |
| **MS-01** | material_ledger schema v1 と CRUD CLI | approved | 素材登録・索引・sidecar 紐付け |
| **MS-02** | material_sidecar schema v1 と validator | approved | 出典・ライセンス・利用条件の必須化 |
| **MS-03** | 透過PNG 受け入れフロー | approved | 外部処理（または人手）で生成された透過PNG を ledger に登録、sidecar 強制 |
| **TH-01** | YMM4 サムネ slot patch（NLMYTGen CLI bridge） | approved | NLMYTGen の `patch-thumbnail-template` / `audit-thumbnail-template` を subprocess 経由で呼び、`thumb.image.*` / `thumb.text.*` を patch、readback を返す |
| **SH-01** | CLI runner と config（NLMYTGen path 設定含む） | approved | `config/nlmytgen_path.json`、subprocess wrapper、エラー伝搬 |

## Slice 2 以降の候補（着手前、proposed のまま）

### Editing 系

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| ED-01 | edit_pack schema v1 | proposed | cut EDL／字幕案／配置データの統合 schema |
| ED-02 | カット候補抽出（音声・字幕ベース） | proposed | 元動画から発話単位や字幕タイミングで cut 候補を出す |
| ED-03 | 文脈チェック | proposed | カット境界が話者発話を不自然に切断していないか判定 |
| ED-04 | 字幕案生成 | proposed | テキスト＋タイミング、burned-in 用 |
| ED-05 | 字幕表示幅計測（NLMYTGen CLI bridge） | proposed | NLMYTGen の text_measure を subprocess で利用 |
| ED-06 | 外部 NLE 用 export（EDL／XML） | proposed | DaVinci Resolve / Premiere 向け export |

### Publishing 系

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| PB-01 | publish_draft schema v1 | proposed | metadata（タイトル・説明・タグ・category）の整形 |
| PB-02 | private/unlisted upload integration | proposed | `src/integrations/youtube/` 経由 |
| PB-03 | thumbnail 設定 integration | proposed | `thumbnails.set` |
| PB-04 | upload receipt 記録 | proposed | `upload_receipt.json` |

### Integrations

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| INT-01 | YouTube OAuth flow | proposed | trusted application のセットアップ含む |
| INT-02 | asset_fetch（VOD 取得） | proposed | yt-dlp 系ラッパー、Compliance gate 必須 |
| INT-03 | bg_removal 受領フロー | proposed | 外部処理結果（透過PNG）の受け入れ。API 呼び出しは含めるか別途検討 |
| INT-04 | bg_removal API 呼び出し | proposed | INT-03 の能動版。外部送信を伴うため危険度中、要ユーザー承認 |

### Shared infra

| ID | 機能 | 状態 | 概要 |
|---|---|---|---|
| SH-02 | episode_pack 統合 manifest | proposed | rights_manifest / material_ledger / edit_pack / thumbnail_patch / publish_draft を episode 単位で連結 |
| SH-03 | GUI（最小） | proposed | 4レーンを扱う最小 GUI。**NLMYTGen GUI（Electron）と操作感・タブ構造・配色・ナビゲーション規約を揃える**。技術スタックは NLMYTGen と同じ Electron を第1候補。Slice 1 では作らず、Slice 2 以降で着手 |
| SH-04 | NLMYTGen GUI への逆提案運用 | proposed | ClipPipeGen で得た GUI 知見（lane 分離・gate 強制 UI・readback 表示等）を NLMYTGen 側に doc／issue ベースで提案する運用。NLMYTGen 側ファイルの直接編集は行わない |

## 永続スコープ外（rejected / 永続）

| ID | 機能 | 状態 | 理由 |
|---|---|---|---|
| OUT-01 | 動画レンダリング（cut/concat/字幕焼き込み／エンコード） | rejected（永続） | INVARIANTS：YMM4／外部 NLE／人手の責務 |
| OUT-02 | 音声合成（TTS） | rejected（永続） | 元動画の音声を使うのが本ツールの前提 |
| OUT-03 | 自動公開（public 化） | rejected（永続） | INVARIANTS：永続手動 gate |
| OUT-04 | 完全自動サムネ合成 | rejected（永続） | INVARIANTS：構図・配色・最終クリック感は YMM4 上の人手判断 |
| OUT-05 | `.ymmp` ゼロ生成 | rejected（永続） | INVARIANTS：YMM4 互換性を壊す |
| OUT-06 | NLMYTGen 側ファイル編集 | rejected（永続） | INVARIANTS：別リポの North Star を濁さない |

## 状態遷移ログ

（slice ごとに、状態遷移の根拠を1行で残す）

- bootstrap: 全項目を `proposed` で起票。根拠: docs/FIRST_SLICE.md / docs/LANES.md
- 2026-05-06: Slice 1 の `CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01` を `approved` に昇格。根拠: ユーザー指示（軽量 review 後の着手承認）
