# Invariants

破ってはいけない条件・責務境界を保持する正本。理由付きで残す。

## North Star

- **元動画は人間が権利確認した素材**が前提。Python が無条件取得・無条件投稿することはない。
- **Python は接着層**：EDL／字幕案／manifest／slot patch までを担う。動画レンダリング・字幕焼き込み・音声合成・公開判断は本体外。
- **最終生成は YMM4／外部 NLE／人手**で完結する。Python から動画ファイルを生成しない。
- **公開は永続的に手動 gate**。Python が `public` に切り替えるパスを持たない。

## Production Value North Star

- 制作価値は **「権利確認済みの元動画を、字幕／配置／サムネ込みで public 化候補（private/unlisted）まで運べる」** ことで測る。
- preflight が通る・schema が validate する・テストが通るは接続証跡であり、成果そのものではない。
- レーン横断の成果は `episode_pack.{id, rights_manifest, material_ledger, edit_pack, thumbnail_patch, publish_draft}` がすべて連結された状態で測る。

## 責務境界

- **Compliance / Rights は決定層**。`compliance_check.status` は他レーンへの gate として機能する。compliance を経由せずに upload／publish へ進むパスを作らない。
- **Material Sourcing は横断レイヤー**。Editing／Thumbnail／Compliance がそれぞれ素材要求を出し、Material Sourcing が一元的に台帳化する。動画編集配下に置かない。
- **Editing は cut EDL／字幕案／配置データまで**。動画ファイルの cut 実行・concat・字幕焼き込みは外部 NLE／YMM4／人手で行う。
- **Thumbnail は YMM4 サムネテンプレへの slot patch まで**。文字＋立ち絵の完全自動合成、構図・配色・最終クリック感の自動決定は v1 ではやらない。
- **Publishing は private/unlisted upload と metadata／thumbnail 設定まで**。公開ボタンは永続手動 gate。

## Integrations 隔離

外部 API・AI・取得系は **`src/integrations/` の中に隔離**する。本体ロジックは integration 結果を受け取るだけ。

- `src/integrations/youtube/` — OAuth・videos.insert・thumbnails.set
- `src/integrations/asset_fetch/` — 元動画／VOD 取得
- `src/integrations/bg_removal/` — 背景切り抜き API（外部送信を伴う）

本体は透過PNG＋出典 sidecar を **受け取る** 形で接続する。本体に外部送信ロジックを直書きしない。

## NLMYTGen との関係

- **NLMYTGen のファイルは読まない・書かない・編集しない**。
- 再利用は CLI subprocess 経由のみ：`patch-thumbnail-template` / `audit-thumbnail-template` / 字幕表示幅計測。
- shared package 化は先回しでやらない。CLI bridge で運用感を見てから判断する。
- NLMYTGen 側の E-01（YouTube投稿）への依存を作らない。本リポ独自の `src/integrations/youtube/` を持つ。NLMYTGen 側で E-01 が successor-lane で起票されるかは本リポの判断対象外。

## Prohibited Interpretations / Shortcuts

- **`compliance_check.status != passed` の manifest／素材を upload／publish 系 CLI に渡さない**。理由: 権利侵害投稿は事故になり、削除・チャンネル停止・法的リスクを伴う。
- **自動公開はしない**。CLI に `--publish` `--public` のような flag を追加しない。理由: 公開は人間判断であり、誤公開のロールバックコストが極めて高い。
- **`.ymmp` をゼロから生成しない**。YMM4 で人間が用意したベース／テンプレへの限定 patch のみ。理由: ymmp スキーマは YMM4 のバージョンに従属し、ゼロ生成は YMM4 互換性を失う。
- **背景切り抜き AI を本体ロジックに直書きしない**。`src/integrations/bg_removal/` 経由で結果を受け取る。理由: API 規約・課金・送信画像の権利・モデル切り替えが全て integration 境界の中で済む構造にする。
- **元動画を無確認でダウンロードしない**。VOD 公開状態と利用条件のチェック後にのみ取得する。理由: メンバー限定動画・削除動画・規約違反動画の取得は事故源。
- **完全自動サムネ合成をやらない**。文字＋立ち絵の構図・配色・最終クリック感は YMM4 上の人手判断を残す。理由: サムネはクリック率に直結するクリエイティブ判断であり、定型化は競争力低下を招く。
- **NLMYTGen の docs／runtime-state／INVARIANTS／コードを編集しない**。再利用は CLI 経由のみ。理由: NLMYTGen は別 North Star を持つ独立リポであり、本リポの変更で NLMYTGen の主軸が濁ることを避ける。
- **shared package を先回しで作らない**。理由: 再利用パターンが固まる前の抽象化は死荷重になる。CLI subprocess で 2-3 個の実例が出てから判断する。

## Compliance Gate（強制ゲート仕様）

以下の操作は `rights_manifest.compliance_check.status == "passed"` を **CLI 引数の必須前提** とする。enforcement は schema validator＋CLI runner で行う。

- 元動画ダウンロード（`src/integrations/asset_fetch/`）
- YouTube upload（`src/integrations/youtube/`、private/unlisted 含む）
- thumbnail 設定（`src/integrations/youtube/thumbnails.set`）
- 公開可否を含む metadata draft の確定書き出し

`status != passed` の場合は CLI が早期失敗し、エラー内容を `compliance_check.errors[]` から表示する。

## 運用ルール

- ユーザーが一度説明した非交渉条件は本ファイルに固定する。
- 理由を「Why:」として 1 行残す。後でエッジケース判断ができるようにする。
- 日付固定の宣言（「2026-xx-xx 固定」等）は使わない。状態は [docs/RUNTIME_STATE.md](RUNTIME_STATE.md) に置く。

## 意思決定注記の最小仕様

対象: 新方針採用 / 方針撤回 / 主軸・slice・next_action 変更 / FEATURE status 遷移。
形式: `根拠: <源1> [+ <源2>]`
許容源: canonical docs 参照 / FEATURE ID / DECISION LOG 行。
禁止源: 「経験的に」「一般に」「安全上」など verifiable でない抽象文言。
