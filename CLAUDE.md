# CLAUDE.md — ClipPipeGen プロジェクト方針

このファイルはプロジェクトの方針・技術スタック・成功定義を定める。運用ルールの正本は [docs/INVARIANTS.md](docs/INVARIANTS.md) と [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)。エージェント入口は [AGENTS.md](AGENTS.md)。

## プロジェクト概要

ホロライブ等の VTuber 切り抜き動画制作を、**権利・素材・編集・サムネ・投稿の4レーン**で半自動化する制作補助ツール。元動画 → rights → cut EDL → 字幕案 → サムネ slot patch → private upload までを Python で接着し、最終生成と公開判断は YMM4／外部 NLE／人手で行う。

## 技術スタック

- Python（stdlib 優先。外部依存は integration（YouTube API / 背景切り抜き）境界の中だけに限定する）
- pytest（テスト。実装が入ってから最小セットを起こす）
- YMM4（サムネテンプレ・場合により動画タイムライン用ベース。外部ツール、Python では操作しない）
- 外部 NLE（DaVinci Resolve / Premiere 等。EDL/XML 経由のハンドオフ。本体は操作しない）

## 成功定義（v1）

1. 1本の元動画 URL に対して、`rights_manifest` が `compliance_check.status=passed` で確定できる
2. その動画用の素材（人物画像・背景・ロゴ・出典）が `material_ledger` に登録され、それぞれ出典・利用条件 sidecar を持つ
3. 透過PNG として受領した人物素材が、YMM4 サムネテンプレの `thumb.image.*` slot に patch される
4. `thumb.text.*` slot にテキストが patch される
5. 上記の readback（どの素材がどの slot に入ったか）が manifest として残る
6. **`compliance_check.status != passed` の素材／manifest は upload／publish 系 CLI に渡せない**（gate enforcement）

動画 cut detection・字幕生成・YouTube upload は v1 のスコープ外（後続 slice）。

## 絶対的な制約

- **動画レンダリング・字幕焼き込み・音声合成を Python 本体ではやらない**
- **公開ボタンは永続的に手動 gate**。自動公開はスコープ外。private/unlisted upload までで止める
- **`.ymmp` ゼロ生成は禁止**。YMM4 で人間が用意したベース／テンプレへの限定 patch に留める
- **`compliance_check.status != passed` の素材は upload／publish 系に渡さない**
- **背景切り抜き AI・元動画取得は integration 境界（`src/integrations/`）の中に隔離**。本体は透過PNG＋出典 sidecar を受け取る形で接続する
- **文字＋立ち絵の完全自動合成・構図・配色・最終クリック感の自動決定は v1 ではやらない**。サムネは YMM4 上の人手判断を残す
- **NLMYTGen の docs／runtime-state／INVARIANTS／コードは触らない**。再利用は CLI subprocess 経由のみ
- **shared package 化を先回しでやらない**。CLI bridge で運用感を見てから判断する

## NLMYTGen との関係

- 別リポ。**GUI アプリは共有しないが、見た目・操作感・タブ構造は NLMYTGen GUI に合わせる**。Electron スタック・配色・ナビゲーション規約・タブ構成・readback 表示パターンは揃える。理由: ユーザーが両ツールを同じ操作感で使えるようにする。
- **双方向改善を許容**：ClipPipeGen 側で得た知見（lane 分離・gate 強制・readback 表示等）は NLMYTGen 側 GUI への逆提案として共有可能。逆も同じ。ただし NLMYTGen 側ファイルの直接編集はしない。提案は doc／issue ベースで行う。
- 再利用は CLI subprocess 経由：
  - `patch-thumbnail-template` / `audit-thumbnail-template`（サムネ slot patch）
  - 字幕表示幅計測（将来：Editing レーン burned-in 字幕の幅制御）
  - `build-session-manifest`（schema 構造の参考のみ。データは共有しない）
- NLMYTGen 側の E-01（YouTube投稿）は現在 `hold`。ClipPipeGen 側で integration point が具体化したら、NLMYTGen 側で successor-lane として起票してもらう（本リポからは要求しない、依存を作らない）。

## 4レーン（要約）

詳細は [docs/LANES.md](docs/LANES.md)。

| レーン | 責務 | 主成果物 |
|---|---|---|
| Compliance / Rights | 権利確認・公開可否ゲート | `rights_manifest.json` |
| Material Sourcing（横断） | 素材取得・背景切り抜き受領・素材台帳 | `material_ledger.json` / 透過PNG＋sidecar |
| Editing | カット候補・字幕案・配置データ | `edit_pack.json` |
| Thumbnail | YMM4 サムネ slot patch | patched `.ymmp` |
| Publishing（Compliance 内 gate） | metadata draft・private upload | `publish_draft.json` |

## 機能追加のルール

- [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md) が全件把握の唯一のソース
- 登録されていない機能は追加しない
- `proposed` ステータスの機能はユーザー承認後に `approved` へ昇格してから実装する
- 自動化の境界は [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md) に従う

## ドキュメント構成

| ファイル | 責務 |
|---|---|
| README.md | プロジェクトの入口 |
| CLAUDE.md（本ファイル） | 方針・技術スタック・成功定義・絶対的な制約 |
| AGENTS.md | AI エージェント入口・read order |
| .claude/CLAUDE.md | Claude Code 用入口（薄いポインタ） |
| docs/INVARIANTS.md | 非交渉条件・責務境界 |
| docs/LANES.md | 4レーンの責務境界詳細 |
| docs/AUTOMATION_BOUNDARY.md | やる／やらないの境界・手動 gate の所在 |
| docs/RUNTIME_STATE.md | 現在位置・次の手 |
| docs/FEATURE_REGISTRY.md | 機能一覧（全件） |
| docs/FIRST_SLICE.md | Slice 1 設計 |
| docs/SCHEMAS/v1/*.md | v1 schema 定義（rights_manifest / material_ledger / material_sidecar / thumbnail_patch_input / edit_pack） |

## スコープ外（v1）

- 動画 cut detection の実装（後続 slice）
- 字幕生成・字幕焼き込み（後続 slice）
- YouTube API 投稿（後続 slice。private/unlisted まで）
- 完全自動サムネ合成（永続的にスコープ外）
- 自動公開（永続的にスコープ外）
- 他プラットフォーム（X／Bilibili 等）への投稿
- ライブ配信切り抜き以外の用途（楽曲MV切り抜き等は権利モデルが違うので別途検討）
