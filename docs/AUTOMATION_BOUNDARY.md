# Automation Boundary

何を自動化し、何を人手・外部ツールに残すかの境界。手動 gate の所在と危険度マップが正本。

## 危険度マップ

| 危険度 | 操作 | 場所 | 制約 |
|---|---|---|---|
| **最高** | YouTube 動画の公開（public 化） | YouTube Studio（人手） | 永続手動 gate。Python は touch しない |
| **高** | YouTube への upload | `src/integrations/youtube/` | private/unlisted のみ。`compliance_check.status==passed` 必須。ユーザー確認を取って実行 |
| **高** | 元動画ダウンロード | `src/integrations/asset_fetch/` | VOD 公開状態と利用条件チェック後のみ。ユーザー確認を取って実行 |
| **中** | 背景切り抜き API 呼び出し | `src/integrations/bg_removal/` | 外部 API へ画像を送信する。送信前にユーザー確認 |
| **中** | サムネ slot patch 適用（書き出し） | `src/cli/patch_thumbnail.py`（NLMYTGen CLI bridge 経由） | 上書きせずコピー先へ書く。元ファイル保持 |
| **低** | manifest／schema validate | `src/pipeline/*` | ローカルファイル読み書きのみ |

## やる（v1 スコープ内）

- 元動画 URL に対する `rights_manifest` 構造化（人手入力中心、整形と validate のみ自動）
- 素材の台帳化（`material_ledger`）と sidecar 強制
- 透過PNG（人物画像）の受け入れと slot 配置
- YMM4 サムネテンプレへの `thumb.image.*` / `thumb.text.*` slot patch（NLMYTGen CLI bridge 経由）
- Compliance gate 強制（`status != passed` の素材／manifest を upload／publish 系に渡せない CLI 設計）
- 後続スライスで段階的に追加（FEATURE_REGISTRY 参照）：
  - 元動画ダウンロード integration（VOD 公開状態 gate 付き）
  - カット候補抽出（`edit_pack.cut_candidates`）
  - 字幕案生成（`edit_pack.subtitles`）
  - private/unlisted upload integration

## やらない（永続スコープ外）

- **動画レンダリング**：cut/concat/字幕焼き込み／エンコードは Python 本体で行わない。YMM4／外部 NLE／人手。
- **音声合成**：本ツールは元動画の音声をそのまま使う。TTS は組み込まない。
- **公開（public 化）**：永続手動 gate。CLI に `--publish` `--public` flag を追加しない。
- **完全自動サムネ合成**：文字＋立ち絵の構図・配色・最終クリック感の自動決定はやらない。サムネは YMM4 上の人手判断を残す。
- **`.ymmp` ゼロ生成**：YMM4 で人間が用意したベース／テンプレへの限定 patch のみ。
- **NLMYTGen 側ファイルの編集**：再利用は CLI subprocess 経由のみ。
- **他プラットフォーム投稿**（X／Bilibili 等）：v1 スコープ外。要件が出たら別途検討。
- **コメント自動応答／タグ自動最適化／収益化設定切替**：投稿後の運用は人手。
- **ライブ配信切り抜き以外の用途**（楽曲 MV 切り抜き等）：権利モデルが違うので別途検討。

## 手動 gate の所在

ここに該当する操作は、**Python が自動で完了させない**：

1. **公開（public 化）** — YouTube Studio で人手実行
2. **元動画の利用可否最終判断** — `compliance_check.status` を `passed` にするのは人手判断（CLI は項目チェックのみ補助）
3. **サムネの構図・配色・テキスト最終確認** — YMM4 上で人手調整
4. **upload 前の動画ファイル確認** — YMM4／外部 NLE で書き出した動画を人手で確認後、ファイルパスを CLI に渡す
5. **private → unlisted → public への昇格** — 各段階で人手確認

## Compliance Gate の強制機構

以下の CLI は引数として `--rights-manifest PATH` を必須とし、`compliance_check.status == "passed"` を CLI runner 側で validate する：

- 元動画ダウンロード CLI（`fetch-source-video`）
- private upload CLI（`upload-private`）
- thumbnail 設定 CLI（`set-thumbnail`）
- metadata 確定書き出し CLI（`finalize-metadata`）

`status != passed` の場合、CLI は exit 1 で早期失敗し、`compliance_check.errors[]` を表示する。bypass flag は **追加しない**。

## Integrations 隔離方針

`src/integrations/` の中だけが外部送信・課金・規約従属の処理を持つ。本体ロジック（`src/pipeline/`）は integration 結果を受け取るだけ。

| ディレクトリ | 含むもの | 含まないもの |
|---|---|---|
| `src/integrations/youtube/` | OAuth、videos.insert、thumbnails.set、playlist 操作 | 公開（public 化） |
| `src/integrations/asset_fetch/` | yt-dlp 系ラッパー、VOD ダウンロード | 編集処理、規約判定 |
| `src/integrations/bg_removal/` | 背景切り抜き API クライアント、結果ファイル受領 | 元動画への適用、サムネ合成 |
| `src/pipeline/` | manifest／schema／slot patch／validate | 外部送信、課金、認証 |
| `src/cli/` | コマンドライン entry points | 業務ロジック（pipeline 呼び出しのみ） |

## NLMYTGen GUI との整合方針

- **GUI アプリは共有しない**が、見た目・操作感・タブ構造・readback 表示パターンは NLMYTGen GUI に合わせる
- 技術スタックは NLMYTGen と同じ Electron を第1候補（GUI 着手時に再検討）
- ClipPipeGen で得た GUI 知見は **NLMYTGen 側への逆提案として doc／issue ベースで共有**できる。NLMYTGen 側ファイルの直接編集はしない
- GUI そのものは Slice 1 では作らない。CLI 運用感を見てから後続スライス（SH-03）で起票

## NLMYTGen CLI bridge 方針

NLMYTGen は別リポ。以下の方針で再利用する：

- 呼び出しは subprocess（Python の `subprocess.run`）
- NLMYTGen の Python module を直接 import しない
- NLMYTGen のソースコードをコピーしない
- NLMYTGen の絶対パスは設定ファイル（`config/nlmytgen_path.json`）で管理。ハードコードしない
- NLMYTGen が見つからない／バージョン不一致の場合はエラーで止める。silent fallback しない
- NLMYTGen 側 CLI の出力（stdout/JSON）を本リポの schema に変換するのは pipeline 層の責務

bridge する CLI 候補：

- `patch-thumbnail-template`（Slice 1 で使用）
- `audit-thumbnail-template`（Slice 1 で使用）
- 字幕表示幅計測（後続スライスで Editing 用）
