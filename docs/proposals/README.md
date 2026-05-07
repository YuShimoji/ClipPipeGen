# Proposals to NLMYTGen

ClipPipeGen 側の運用で得た知見のうち、NLMYTGen に逆適用する価値があるものを **doc / issue ベースの提案** として置く。FEATURE: `SH-04`。

## 何のための場所か

- ClipPipeGen で機能・規約・パターンを実装してみたら、NLMYTGen 側にも有効そうな共通化ポイントが見えた、というケースを集約する。
- 提案ドラフトは ClipPipeGen 内で書く。**NLMYTGen 側ファイルは編集しない**（INVARIANTS）。
- 提案を NLMYTGen に渡す手段は (a) 該当ファイルを issue 本文として転記する / (b) NLMYTGen 側 PR を NLMYTGen 側で書いてもらう、のいずれか。提案は提案で、採否は NLMYTGen 側の判断。

## 何を置かないか

- ClipPipeGen 内部で完結する設計／TODO（それは [`FEATURE_REGISTRY.md`](../FEATURE_REGISTRY.md) と [`RUNTIME_STATE.md`](../RUNTIME_STATE.md)）
- NLMYTGen の実装そのもの（patch / diff を貼らない、編集しない）
- ユーザー固有のローカル設定（ここは公の提案場所）

## ファイル命名

`<NNNN>-<short-kebab-title>.md`（連番、4桁ゼロ埋め）。

## 各提案の最低構造

```
# <Title>

- 対象: NLMYTGen の <領域>（GUI / docs / CLI / IR / etc.）
- 影響範囲: <既存機能との関係>
- 危険度: <low/mid/high>

## 背景

ClipPipeGen 側でなぜ有効だったか、観察事実。

## 提案

具体的な共通化案。仮の差分・命名規約・schema 等。

## NLMYTGen 側で考えられる落とし込み

- どのファイル相当を読み替える想定か
- 既存機能の置換ではなく追加 or 並置できるか

## 注意点 / 採否判断材料

- 互換性
- スコープ大小
- 関連する NLMYTGen 側 invariant への影響予測
```

## ステータス

提案ファイルの本文上部に状態を1行で持つ：

| 状態 | 意味 |
|---|---|
| `draft` | ClipPipeGen 側で起草中、まだ NLMYTGen に渡していない |
| `shared` | NLMYTGen に共有済み（issue / 口頭 / 別 PR）。フィードバック待ち |
| `accepted` | NLMYTGen 側が採用（一部 / 全部）。ClipPipeGen 側 doc は履歴として残す |
| `declined` | 不採用。理由を本文に追記して残す |
| `superseded` | 後続提案に置き換えられた |

## 関連

- [docs/GUI_CONVENTIONS.md §9](../GUI_CONVENTIONS.md) — 逆提案運用候補一覧
- [docs/INVARIANTS.md](../INVARIANTS.md) — NLMYTGen ファイルを編集しない原則
- [docs/FEATURE_REGISTRY.md](../FEATURE_REGISTRY.md) `SH-04` — この運用そのもの
