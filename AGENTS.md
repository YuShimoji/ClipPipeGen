# AGENTS.md — ClipPipeGen

このファイルは AI エージェントの入口。境界・read order・再アンカリング手順を定める。運用ルールの正本は [docs/INVARIANTS.md](docs/INVARIANTS.md)、自動化境界は [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)。

## スコープ境界

- **本リポは ClipPipeGen のみを扱う**。NLMYTGen を含む他リポのファイルは読まない・書かない。
- ユーザーが cross-project 作業を明示した場合のみ、その明示範囲だけ扱う。
- 再利用は **CLI subprocess 経由のみ**。NLMYTGen のソースコードを直接 import しない、コピーしない。

## 再開時の read order（最小）

1. [README.md](README.md) — 何のプロジェクトか
2. [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) — 現在のスライス・next_action
3. [docs/INVARIANTS.md](docs/INVARIANTS.md) — 非交渉条件
4. [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md) — 何をやるか／やらないか

これで足りない時のみ、必要な該当節だけ追加で読む：

- [docs/LANES.md](docs/LANES.md) — レーン責務の詳細
- [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md) — 機能一覧
- [docs/FIRST_SLICE.md](docs/FIRST_SLICE.md) — 現スライスの実装計画
- [docs/SCHEMAS/v1/*.md](docs/SCHEMAS/v1/) — schema 詳細

## 危険な操作

以下は **必ずユーザー確認を取ってから** 実行する：

- `src/integrations/asset_fetch/` 経由での元動画ダウンロード（VOD 公開状態と利用条件チェック後）
- `src/integrations/youtube/` 経由での upload（private/unlisted のみ。公開は永続手動 gate）
- `src/integrations/bg_removal/` 経由での背景切り抜き API 呼び出し（外部サービスへの画像送信を伴う）
- リモートへの push（本リポ／NLMYTGen どちらも）

## やってはいけないこと

- NLMYTGen 側のファイル編集（CLI 呼び出しは可、編集は不可）
- `.ymmp` ファイルのゼロ生成
- `compliance_check.status != passed` の manifest／素材を upload／publish 系 CLI に渡す
- 動画レンダリング・音声合成・字幕焼き込みを Python 本体に持ち込む
- 自動公開（YouTube 上の動画を public にする）操作

## 命名規則（FEATURE ID）

| プレフィックス | レーン |
|---|---|
| CR-* | Compliance / Rights |
| MS-* | Material Sourcing |
| ED-* | Editing |
| TH-* | Thumbnail |
| PB-* | Publishing |
| INT-* | Integrations（外部 API・AI サービス境界） |
| SH-* | Shared infra（CLI runner・schema validator 等） |

NLMYTGen 側の FEATURE ID（A-* / B-* 等）とは独立。混同しない。

## 状態遷移

- `proposed` — 提案中。実装着手不可。
- `approved` — ユーザー承認済み。実装着手可。
- `in_progress` — 実装中。
- `done` — 実装＋acceptance 完了。
- `hold` — 一時停止。再開条件を明記する。
- `rejected` — 廃止。理由を残す。
- `successor-lane` — 別 ID として後継が起票された。本 ID は閉じる。

## 再アンカリング（context loss 時）

順序：

1. [README.md](README.md) を読む
2. [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) の `current_slice` と `next_action` を確認
3. 現スライスに直接関係する箇所だけ追加で読む
4. 不明点があればユーザーに確認、推測で書かない
