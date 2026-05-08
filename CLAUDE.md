# CLAUDE.md — ClipPipeGen プロジェクト方針

このファイルはプロジェクトの方針・技術スタック・成功定義を定める。運用ルールの正本は [docs/INVARIANTS.md](docs/INVARIANTS.md) と [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)。エージェント入口は [AGENTS.md](AGENTS.md)。

## プロジェクト概要

ホロライブ等の VTuber 切り抜き動画制作を、**rights・素材・編集・サムネ・投稿の4レーン**で半自動化する制作補助ツール。元動画 → 素材取得 → rights 記録 → cut EDL → 字幕案 → サムネ slot patch → upload までを Python で接着する。

## 技術スタック

- Python（stdlib 優先。外部依存は integration（YouTube API / 背景切り抜き）境界の中だけに限定する）
- pytest（テスト。実装が入ってから最小セットを起こす）
- YMM4（サムネテンプレ・場合により動画タイムライン用ベース。外部ツール、Python では操作しない）
- 外部 NLE（DaVinci Resolve / Premiere 等。EDL/XML 経由のハンドオフ。本体は操作しない）

## 成功定義（v1）

1. 1本の元動画 URL に対して、`rights_manifest` が作成・更新・検証できる
2. その動画用の素材（人物画像・背景・ロゴ・出典）が `material_ledger` に登録され、それぞれ出典・利用条件 sidecar を持つ
3. 透過PNG として受領した人物素材が、YMM4 サムネテンプレの `thumb.image.*` slot に patch される
4. `thumb.text.*` slot にテキストが patch される
5. 上記の readback（どの素材がどの slot に入ったか）が manifest として残る
6. `compliance_check.status` や sidecar の source/license/restriction は readback として残り、local CLI の hard gate にならない

動画 cut detection・字幕生成・YouTube upload は後続 slice。

## 絶対的な制約

- **未実装機能を禁止として書かない**。必要なら FEATURE_REGISTRY に起票して実装する
- **rights / sidecar の値だけで実行を止めない**。記録・警告・readback として扱う
- **背景切り抜き AI・元動画取得・YouTube API は integration 境界（`src/integrations/`）の中に隔離**。本体は integration 結果を受け取る形で接続する
- **動画レンダリング・字幕焼き込み・音声合成・完全自動サムネ合成は未実装**。必要になった時点で通常 feature として扱う
- **NLMYTGen の docs／runtime-state／INVARIANTS／コードは触らない**。再利用は CLI subprocess 経由のみ
- **shared package 化を先回しでやらない**。CLI bridge で運用感を見てから判断する

## NLMYTGen との関係

- 別リポ。**GUI アプリは共有しないが、見た目・操作感・タブ構造は NLMYTGen GUI に合わせる**。Electron スタック・配色・ナビゲーション規約・タブ構成・readback 表示パターンは揃える。理由: ユーザーが両ツールを同じ操作感で使えるようにする。
- **双方向改善を許容**：ClipPipeGen 側で得た知見（lane 分離・readback 表示・状態語彙等）は NLMYTGen 側 GUI への逆提案として共有可能。逆も同じ。ただし NLMYTGen 側ファイルの直接編集はしない。提案は doc／issue ベースで行う。
- 再利用は CLI subprocess 経由：
  - `patch-thumbnail-template` / `audit-thumbnail-template`（サムネ slot patch）
  - 字幕表示幅計測（将来：Editing レーン burned-in 字幕の幅制御）
  - `build-session-manifest`（schema 構造の参考のみ。データは共有しない）
- NLMYTGen 側の E-01（YouTube投稿）は現在 `hold`。ClipPipeGen 側で integration point が具体化したら、NLMYTGen 側で successor-lane として起票してもらう（本リポからは要求しない、依存を作らない）。

## 4レーン（要約）

詳細は [docs/LANES.md](docs/LANES.md)。

| レーン | 責務 | 主成果物 |
|---|---|---|
| Compliance / Rights | 権利・出典・状態の記録 | `rights_manifest.json` |
| Material Sourcing（横断） | 素材取得・背景切り抜き受領・素材台帳 | `material_ledger.json` / 透過PNG＋sidecar |
| Editing | カット候補・字幕案・配置データ | `edit_pack.json` |
| Thumbnail | YMM4 サムネ slot patch | patched `.ymmp` |
| Publishing | metadata draft・upload | `publish_draft.json` |

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
| docs/AUTOMATION_BOUNDARY.md | integration マップ・実装済／未実装の区分・readback の所在 |
| docs/RUNTIME_STATE.md | 現在位置・次の手 |
| docs/FEATURE_REGISTRY.md | 機能一覧（全件） |
| docs/FIRST_SLICE.md | Slice 1 設計 |
| docs/SCHEMAS/v1/*.md | v1 schema 定義（rights_manifest / material_ledger / material_sidecar / thumbnail_patch_input / edit_pack / transcript） |

## 未実装の主要機能（実装対象、起票先 [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md)）

- 動画 cut detection（ED-02）
- 実 STT engine 接続（ED-07 successor、whisper.cpp 等）
- 文脈チェック（ED-03）
- 字幕案生成（ED-04）
- NLE export（ED-06）
- source audio / video 取得 integration（INT-02）
- 背景切り抜き API integration（INT-04）
- YouTube OAuth + upload + thumbnail 設定 + visibility 更新（INT-01 / PB-01..04）
- 完全自動サムネ合成（OUT-04）
- 動画レンダリング / 音声合成（OUT-01 / OUT-02）

未実装は実装対象として登録する。未実装イコール禁止ではない。
