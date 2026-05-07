# 0001 — GUI alignment suggestions from ClipPipeGen MVP

- 状態: `draft`
- 対象: NLMYTGen の GUI（Electron）／operator console 周辺
- 影響範囲: 既存 GUI tab 構造との並置、状態語彙、readback 表示
- 危険度: low（互換性破壊なし、追加レイヤとして共存可）

## 背景

ClipPipeGen Slice 2 で operator console（GUI MVP Phase 1）を実装した。少数 episode を扱う薄い表示層だが、以下のパターンが「共通化できそう」と感じられた。

ClipPipeGen 側の関連実装：

- `src/pipeline/episode_status.py` — artifact 存在 / lane state / next_action を一元化する adapter
- `src/cli/status_episode.py` — それを GUI に渡す JSON CLI
- `gui/main.cjs` + `gui/renderer.{html,js}` — 5 タブ構成の operator console
- `docs/GUI_CONVENTIONS.md` — 整合-A 規約

両ツールとも YMM4 + 人手判断を中心に置きながら、Python が薄い接着層として動く点で運用形が近い。GUI レイヤだけでも語彙・パターンが揃うと、ユーザーが両ツールを行き来したときの認知負荷が下がる。

## 提案

以下4点を NLMYTGen GUI と共通化する案として並べる。各項目は独立採否可。

### 1. lane state 語彙の統一

operator が見る最上位状態を 4 値に揃える：

| state | 意味 |
|---|---|
| `ready` | 次工程に進める |
| `blocked` | schema / audit / file resolution でブロック |
| `manual_needed` | 入力・素材・外部 artifact など次の材料が要る |
| `missing` | 該当 artifact が未配置 |

ClipPipeGen 側 schema: `episode_status.<lane>.state` で上記 4 値を返す。

### 2. 多段 readback の独立セクション表示

複数段の検証（compliance → material → audit → patch → readback など）を **段ごとに独立セクション** で出す。1段でも fail したら後段は表示するが結果を出さない（前段 fail を上書きしない）。

ClipPipeGen 側 schema: `thumbnail_patch_result` の rights readback / material_validation / audit_result / patch_result.applied_slots[] を GUI でセクション分けしている。

NLMYTGen 側で類似の多段フローがあれば（例: `apply-production` の skit_group preflight / placement / readback 等）、同じ section 分割パターンを Settings／Production タブに導入する。

### 3. local config readiness の Settings タブ提示

ClipPipeGen は `config/nlmytgen_path.json` の存在 / 構造妥当性 / `nlmytgen_root` 解決可否を Settings タブで一行表示する：

```
ready: yes / no
message: "NLMYTGen bridge config looks ready" or specific failure reason
```

NLMYTGen 側にもローカル設定（YMM4 path、template root、tachie motion map library 等）があるはず。Settings タブで「ready / not ready ＋ 1行 message」を並べると、ユーザーが起動直後の readiness を一目で判断できる。

### 4. 未実装 action の「ボタンを置かない」原則

ClipPipeGen の GUI MVP では、未実装の upload / external API / asset fetch / bg-removal 送信に **disabled button を置いていない**。禁止ではなく、実体のない操作を置かない方針。

NLMYTGen 側でも、明らかに人手判断のはずの操作（YMM4 制作確認・creative acceptance 等）は GUI ボタン化しない方が境界が崩れにくい。

## NLMYTGen 側で考えられる落とし込み

| ClipPipeGen 側 | NLMYTGen 側で見られそうな対応箇所（推測） |
|---|---|
| `episode_status.<lane>.state` 語彙 | `runtime-state.md` の lane / status 語彙、FEATURE_REGISTRY status |
| 多段 readback セクション | `apply-production` の readback 表示、`patch-ymmp` の `file_readback` |
| Settings tab readiness | bridge / template / motion library 設定の起動時チェック |
| 未実装 action button 不在 | GUI 上の制作確認ボタンの有無方針 |

具体的な NLMYTGen 側ファイルの差分は提示しない（INVARIANTS：NLMYTGen ファイルを編集しない）。NLMYTGen 側で採用する場合は NLMYTGen 側の判断で実装する。

## 注意点 / 採否判断材料

- 互換性: 4項目とも GUI 表示層の改善で、CLI / pipeline / schema には触らない。既存機能と並置可能。
- スコープ: 4項目は粒度がバラバラ。lane state 語彙統一は最も小さく即効、未実装 action button 不在は表示方針なので合意までで足りる。多段 readback セクションは UI 改修コスト中、Settings readiness は ClipPipeGen 側にあるパターンの移植で済む。
- NLMYTGen 側 invariant 影響: 既存「YMM4 が制作基盤」「Python は接着層」と整合する。GUI が追加機能を持つわけではなく、表示の整理のみ。

## 残タスク

- [ ] NLMYTGen 側に共有（issue / 口頭）→ 状態を `shared` に
- [ ] NLMYTGen 側からのフィードバックを本ファイル末尾に追記
- [ ] 採否確定後、状態を `accepted` / `declined` に更新（ClipPipeGen 側 doc は履歴として残す）
