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
| `--manual` | `#9a6a17` | state=manual_needed / review note |
| `--blocked` | `#ad3d3a` | state=blocked / structural failure |
| `--missing` | `#617080` | state=missing |

## 2. 状態語彙（lane state）

`status-episode` の各 lane が返す state は以下を共通使用する：

| state | 意味 | 視覚 |
|---|---|---|
| `ready` | 次工程に進める | 緑バッジ |
| `blocked` | schema / audit / file resolution で進めない | 赤バッジ |
| `manual_needed` | 入力・素材・外部 artifact など次の材料が要る | 黄バッジ |
| `missing` | 該当 artifact が未配置 | グレーバッジ |

NLMYTGen 側にも同じ語彙を提案する（lane / readback 状態表示の共通化）。

## 3. タブ命名規約

- 主軸 4 レーン + 設定 = タブ並び順は左から **Episode / Rights / Materials / Thumbnail / Settings**
- Editing / Publishing は実装済み範囲だけ tab に出す。未実装 action は禁止ではなく未実装として扱う。
- レーン名は英語短称で揃える（NLMYTGen と並べた時の視覚一貫性のため）。

## 4. readback 表示パターン

- 多段処理（rights readback → material → audit → patch → readback など）は **段ごとに独立セクション** で表示する
- 1 段でも fail したら、後段は表示するが結果を出さない（前段 fail を上書きしない）
- 各段の error は `code @ field: message` 形式の monospace 1 行
- readback per-slot は table（slot_id / kind / applied / match）

## 5. 実行操作の取扱い

- 未実装の upload / asset fetch / bg-removal は、実装されるまで button を置かない。これは禁止ではなく、実体がない操作を置かないという UI 原則。
- ローカル操作（`set-compliance`、`register-material`、`patch-thumbnail`）は **確認 dialog** を経由する（Phase 2 / SH-03b）。dialog には次の3要素を出す:
  - **command 文字列**（`python -m src.cli.main <subcommand>` と渡す引数の要約）
  - **summary**（ローカル CLI かどうか、network call の有無）
  - **reason**（何を更新・生成・readback するか）
- 確認 dialog を経て実行した結果は、各 form 直下の `action-result` 領域に `$ command / exit / stdout tail / stderr tail` の形で出す。stack trace を出さない、長い出力は末尾 N 行に丸める
- 実行後は自動で `status-episode` を refresh して lane state badge を更新する

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
- 未実装 action を disabled button として置かない原則
