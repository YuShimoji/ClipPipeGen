# ClipPipeGen

ホロライブ等の VTuber 切り抜き動画制作を、権利・素材・編集・サムネ・投稿の4レーンで半自動化する制作補助ツール。

## このリポジトリの位置付け

- 元動画 → 権利確認 → カット候補 → 字幕案 → サムネ slot patch → private upload までを接着する Python ツール群。
- 動画レンダリング・字幕焼き込み・音声合成・公開判断は本体の責務外。最終生成は YMM4 / 外部 NLE / 人手で行う。
- [NLMYTGen](https://github.com/YuShimoji/NLMYTGen) とは別リポ。共有は CLI / schema / module 単位のみ。GUI は共有しない。

## 4レーン

| レーン | 責務 | 主成果物 |
|---|---|---|
| Compliance / Rights | 権利確認・公開可否ゲート | `rights_manifest.json` |
| Material Sourcing | 素材取得・背景切り抜き受領・素材台帳（横断レイヤー） | `material_ledger.json` / 透過PNG＋sidecar |
| Editing | カット候補・字幕案・YMM4/NLE 配置データ | `edit_pack.json` |
| Thumbnail | YMM4 サムネテンプレ slot patch | patched `.ymmp` |
| Publishing（Compliance 内 gate） | metadata draft・private/unlisted upload | `publish_draft.json` |

詳細: [docs/LANES.md](docs/LANES.md)

## North Star

- 元動画は **人間が権利確認した素材** が前提。Python が無条件取得・無条件投稿を行うことはない。
- Python は **EDL／字幕案／manifest／slot patch までの接着層**。動画生成・公開判断はしない。
- **公開ボタンは永続的に手動 gate**。自動公開はスコープ外。
- **`.ymmp` ゼロ生成は禁止**。YMM4 で人間が用意したベース／テンプレへの限定 patch に留める。

詳細: [docs/INVARIANTS.md](docs/INVARIANTS.md) / [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)

## 現在のスライス

**Slice 1 ソフト実装は done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）。end-to-end walkthrough は `docs/walkthrough/` で支援。

詳細: [docs/FIRST_SLICE.md](docs/FIRST_SLICE.md) / [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md)

## 1 episode 通し手順

[docs/walkthrough/SLICE1_WALKTHROUGH.md](docs/walkthrough/SLICE1_WALKTHROUGH.md) — `init-episode` から `patch-thumbnail` までの 11 ステップ runbook。
[docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md](docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) — YMM4 上で `thumb.*` Remark 付き base template を authoring する手順。

## 入口

- 運用ルール正本: [docs/INVARIANTS.md](docs/INVARIANTS.md) / [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)
- 機能一覧（全件把握）: [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md)
- 現在位置: [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md)
- GUI MVP: [docs/GUI_MVP_SCOPE.md](docs/GUI_MVP_SCOPE.md)
- AI エージェント入口: [AGENTS.md](AGENTS.md)
