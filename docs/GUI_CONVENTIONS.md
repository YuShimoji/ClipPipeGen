# GUI Conventions

ClipPipeGen と NLMYTGen の **GUI を共有しない** が、見た目・操作感・タブ構造・readback 表示パターンを揃えるための最低限の規約（[CLAUDE.md](../CLAUDE.md) の整合方針 = 整合-A）。コードは独立、規約だけ揃える。

NLMYTGen 側コードを読まずに、両方が独立して合致できるレベルで規定する。NLMYTGen 側で違いが見つかったら、**doc / issue ベースで逆提案**する（NLMYTGen ファイルは編集しない）。

## 1. 配色（light）

ClipPipeGen GUI MVP は warm light scheme を採用する。`gui/styles.css` の `:root` カスタムプロパティが正本。

| 役割 | 値 | 用途 |
|---|---|---|
| `--bg` | `#f6f4ef` | 背景（warm cream） |
| `--surface` | `#ffffff` | カード / detail パネル |
| `--surface-2` | `#eef4f1` | sidebar / 補助領域 |
| `--ink` | `#20242a` | 通常テキスト |
| `--muted` | `#68727d` | 補助テキスト・ラベル |
| `--line` | `#d8ddd9` | 罫線 |
| `--accent` | `#2768a6` | active tab、focus、ボタン |
| `--accent-2` | `#1d7a83` | secondary accent |
| `--ok` | `#28745a` | state=ready / passed |
| `--manual` | `#9a6a17` | state=manual_needed |
| `--blocked` | `#ad3d3a` | state=blocked / failure |
| `--missing` | `#617080` | state=missing |

## 2. 状態語彙（lane state）

`status-episode` の各 lane が返す state は以下を共通使用する：

| state | 意味 | 視覚 |
|---|---|---|
| `ready` | 次工程に進める | 緑バッジ |
| `blocked` | schema / audit / gate でブロック | 赤バッジ |
| `manual_needed` | 人間判断（compliance gate 等）が要る | 黄バッジ |
| `missing` | 該当 artifact が未配置 | グレーバッジ |

NLMYTGen 側にも同じ語彙を提案する（lane / gate 状態表示の共通化）。

## 3. タブ命名規約

- 主軸 4 レーン + 設定 = タブ並び順は左から **Episode / Rights / Materials / Thumbnail / Settings**
- Editing / Publishing は **未実装の段階では tab を出さない**（disabled でも置かない、placeholder も置かない）。GUI に出すと操作可能に見える。
- レーン名は英語短称で揃える（NLMYTGen と並べた時の視覚一貫性のため）。

## 4. readback 表示パターン

- 多段検証（compliance → material → audit → patch → readback など）は **段ごとに独立セクション** で表示する
- 1 段でも fail したら、後段は表示するが結果を出さない（前段 fail を上書きしない）
- 各段の error は `code @ field: message` 形式の monospace 1 行
- readback per-slot は table（slot_id / kind / applied / match）

## 5. 危険操作の取扱い

- 永続手動 gate（自動公開、元動画ダウンロード、外部 API 送信）は **そもそも button を置かない**。disabled にすらしない（誘惑させない）
- ローカルだが高影響の操作（`set-compliance --status passed`、`register-material`、`patch-thumbnail`）は確認 dialog を必須とする（Phase 2 / SH-03b）

## 6. レイアウト原則

- 最初の画面は dashboard（episode 一覧）。landing / splash は作らない
- detail ペインは選択された episode 1 つに対する表示。複数 episode 同時編集はしない
- footer は status bar（直近 1 行のみ）。stack trace を出さない

## 7. ファイル参照表示

- artifact path は monospace、相対パスを優先（リポ root からの相対）
- 「Reveal in folder」ボタンを置く（OS のファイラで開く。編集はしない）

## 8. 国際化

- v1 は英語＋日本語混在で OK（NLMYTGen と同水準）。完全 i18n は未対応
- 例外文言は code 部分が英語、message 部分はその場の文脈に合わせる

## 9. 逆提案運用

ClipPipeGen 側で得た規約・知見で NLMYTGen 側にも有効そうなものは、`docs/proposals/` 配下に提案文を起こす（後続スライスで実装）。NLMYTGen 側のコードは編集しない。

候補：
- lane 状態語彙の統一（`ready / blocked / manual_needed / missing`）
- 多段 readback の独立セクション表示
- local config readiness の Settings タブ提示
- 危険操作の「button を置かない」原則
