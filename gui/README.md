# ClipPipeGen GUI (MVP / Phase 1)

Slice 1 の artifact を読み取って、episode の状態を見るだけの read-only operator console。Electron 製。

## 構成

```
gui/
├── main.cjs       # Electron main process（spawn `python -m src.cli.main status-episode`）
├── preload.cjs    # contextBridge（window.clipPipe.statusEpisode）
├── renderer.html  # 単一ページ・5 タブ（Episode / Rights / Materials / Thumbnail / Settings）
├── renderer.js    # タブ切替・status カード・detail レンダリング
├── styles.css     # warm light scheme（docs/GUI_CONVENTIONS.md §1 が正本）
├── smoke.cjs      # node 単体での smoke（Electron なしで status-episode JSON shape を確認）
└── README.md
```

`package.json` / `package-lock.json` はリポ root に置く。Electron は `npm install` で `node_modules/` に落とす（gitignored）。

## できること

- 1 episode dir の `rights / materials / thumbnail` lane state（ready / blocked / manual_needed / missing）
- `status-episode` の `next_action`（owner / action / reason）
- `bridge_config` の readiness（Settings タブ）

## できないこと（意図的）

Phase 1 はあえて実行系を持たない。後続 SH-03b（Phase 2）で次の導線を追加予定：

- `set-compliance` 実行
- `register-material` 入力 form
- `patch-thumbnail` 実行 + readback 表示

永続的にやらないこと（INVARIANTS / GUI_MVP_SCOPE）：

- YouTube upload や public 化
- 元動画ダウンロード
- 背景切り抜き API 呼び出し
- `.ymmp` ゼロ生成
- NLMYTGen 側ファイルの編集

## セットアップ

```bash
# リポ root で
npm install
```

`node_modules/` に Electron が入る。lockfile (`package-lock.json`) は repo にコミットする方針（再現性のため）。

## 実行

```bash
# リポ root で
npm start                 # Electron 起動
npm run smoke             # Node 単体 smoke（Electron なし、status-episode JSON shape を確認）
npm run smoke:electron    # Electron を --smoke で起動・即終了（バイナリ動作確認）
```

Python が PATH にない場合は環境変数で指定：

```bash
CLIPPIPEGEN_PYTHON=/path/to/python npm start
```

## 既知の前提

- Python 3.10+ が PATH 上にあるか、`CLIPPIPEGEN_PYTHON` で指定されている
- リポ root の `episodes/<id>/` または `samples/episode_example/` が存在する（`renderer` の Episode dir 入力で指定）
- Settings タブで bridge config の状態が確認できる。`config/nlmytgen_path.json` がない場合は `config/nlmytgen_path.json.example` を参照

## 関連

- [docs/GUI_MVP_SCOPE.md](../docs/GUI_MVP_SCOPE.md) — MVP 範囲
- [docs/GUI_CONVENTIONS.md](../docs/GUI_CONVENTIONS.md) — UI 規約（NLMYTGen 整合用、整合-A）
- [docs/RUNTIME_STATE.md](../docs/RUNTIME_STATE.md) — 現在のスライス
