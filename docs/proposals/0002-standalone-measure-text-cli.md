# 0002 — Standalone `measure-text` CLI for NLMYTGen

- 状態: `draft`
- 対象: NLMYTGen の `src/cli/main.py` / `src/pipeline/text_measure.py`
- 影響範囲: 既存 `build-csv` の measurement 経路は変更不要、追加 CLI のみ
- 危険度: low（read-only、既存出力に影響なし）

## 背景

ClipPipeGen Slice 2 で Editing レーンの burned-in 字幕の幅見積もり機能（ED-05）を実装した。当初は **NLMYTGen の `EastAsianWidthMeasurer` / `WpfTextMeasurer` を CLI subprocess で再利用する設計**で、`docs/RUNTIME_STATE.md` / `docs/FEATURE_REGISTRY.md` にもそう書いていた。

しかし NLMYTGen 側 CLI を確認したところ、`text_measure.py` は class として存在するが **standalone CLI は存在せず**、measurement は `build-csv` に embed されている。`build-csv` を呼ぶと CSV ファイル全体を生成するため、純粋な「文字列 → 幅」用途には重すぎる。

ClipPipeGen 側では **stdlib のみで EAW measurer を再実装**して ED-05 を閉じたが、これは **NLMYTGen との機能重複**になっており、将来の WPF 高精度 measurement や font metrics 反映を共通化できない。

ClipPipeGen 側の関連実装：

- `src/pipeline/text_measure.py` — EAW unit 計算 + 折返し
- `src/cli/measure_subtitle_width.py` — CLI ラッパー

## 提案

NLMYTGen に **`measure-text` standalone CLI を追加**する。既存 `EastAsianWidthMeasurer` / `WpfTextMeasurer` を CLI から利用できるようにするだけで、本体ロジックは変更しない。

### CLI 仕様（提案）

```
python -m src.cli.main measure-text \
  --text "ぺこら、まさかの大爆笑" \
  [--text-file path/to/text.txt] \
  [--backend eaw|wpf] \
  [--font-family "Yu Gothic UI"] \
  [--font-size 36] \
  [--letter-spacing 0] \
  [--wrap-px 1080] \
  [--wrap-eaw 40] \
  [--measure-exe path/to/MeasureTextWpf.exe] \
  [--format text|json]
```

入出力：

- `--text` または `--text-file` のいずれか必須。
- `--backend eaw`（デフォルト、stdlib のみ）または `wpf`（Windows、外部 helper exe）。
- `--wrap-eaw N`：EAW unit ベースの折返し（subtitle planning 用）。
- `--wrap-px N`：実 pixel 折返し（YMM4 layout fidelity 用、`wpf` backend 必須）。
- `--format json` 時の出力構造（提案）：

  ```json
  {
    "text": "...",
    "backend": "eaw",
    "total_chars": 11,
    "total_units": 22,
    "wrap": { "kind": "eaw", "target": 40 },
    "longest_line": { "units": 22, "text": "..." },
    "needs_wrap": false,
    "lines": [
      { "text": "...", "units": 22, "overflows": false }
    ]
  }
  ```

### 期待される統合効果

- ClipPipeGen 側の `src/pipeline/text_measure.py` を **薄い CLI bridge に置き換え**できる。
- NLMYTGen の `build-csv --measure-backend wpf` パイプラインと **同じ measurement** を ClipPipeGen の Editing レーンが使えるようになり、字幕幅の判定が一貫する。
- 将来の font metrics 改善（custom font / line-height / italic 等）を NLMYTGen 側で行えば、ClipPipeGen 側は何もせず追従できる。

## NLMYTGen 側で考えられる落とし込み

| ClipPipeGen 側で観察 | NLMYTGen 側の対応箇所（推測） |
|---|---|
| `measure-text` CLI 追加 | `src/cli/main.py` に subparser、`_cmd_measure_text` ハンドラ |
| 既存 `EastAsianWidthMeasurer` / `WpfTextMeasurer` の利用 | そのまま再利用、新規ロジック不要 |
| `--measure-exe` / `--font-*` / `--wrap-px` などの引数 | `build-csv` と同じ命名規則で揃える |
| 出力 JSON shape | 上記提案を初稿に。NLMYTGen 側で fields 追加・名前変更する判断は OK |

## 注意点 / 採否判断材料

- **互換性**: 追加 CLI のみ。`build-csv` の measurement 経路や YMM4 互換性に影響しない。
- **依存**: WPF backend は既存どおり Windows + `MeasureTextWpf.exe` を要求する。EAW backend は stdlib のみ。
- **DRY**: 採用された場合、ClipPipeGen 側の `text_measure.py` は **bridge 化（薄い subprocess 呼び出し）+ stdlib EAW を fallback** に縮約できる。
- **採用しない場合**: ClipPipeGen は現在の stdlib EAW 実装を維持。WPF 精度は当面手の届かないが、burned-in 字幕の概算幅 / 折返し用途には十分。

## 残タスク

- [ ] NLMYTGen 側に共有（issue / PR）→ 状態を `shared` に
- [ ] NLMYTGen 側で採用された場合、ClipPipeGen 側の `text_measure.py` を bridge に書き換える小スライスを起こす（仮称 `ED-05b: text_measure bridge migration`）
- [ ] 不採用なら本ファイルを `declined` で残し、ClipPipeGen 側は現実装を続行
