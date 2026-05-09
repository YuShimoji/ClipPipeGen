# GUI MVP Scope — Slice 2 / SH-03

ClipPipeGen の最小 GUI は、Slice 1 でできた CLI と manifest を見やすく操作するための operator console とする。NLMYTGen GUI とはアプリを共有しないが、操作感・タブ構造・readback 表示パターンは揃える。

## 決定

- 技術スタックは **Electron** を第1候補として採用する。理由: NLMYTGen GUI と運用感を揃えやすく、将来の逆提案もしやすい。
- GUI は ClipPipeGen リポ内に持つ。NLMYTGen の GUI コードは読まない・コピーしない・編集しない。
- GUI は既存 CLI / pipeline を呼ぶ薄い操作面から始める。外部 API、YouTube upload、元動画ダウンロード、背景切り抜き API 呼び出しは未実装なので MVP には含めない。
- GUI からの `.ymmp` ゼロ生成は未実装。必要になったら別 feature として設計する。

## MVP で扱うレーン

| タブ | 目的 | MVP で表示・実行すること |
|---|---|---|
| Episode | episode の現在状態を一覧する | `rights_manifest` / `material_ledger` / `edit_pack` / `thumbnail_patch_input` / `thumbnail_patch_result` の存在、状態、次に必要な操作 |
| Rights | rights 記録を見える化する | `validate-rights` の結果、`set-compliance` 実行導線、review notes |
| Materials | 素材登録と監査 | `register-material` 入力補助、`audit-material-ledger` 結果、sidecar / hash / transparent PNG check |
| Editing | edit_pack の状態と手動 cut 入力（GUI action は ED-01 / ED-02a の範囲のみ） | `init-edit-pack` / `add-cut-candidate` / `validate-edit-pack` 実行導線、cut_candidates 件数、selected 件数、subtitles 件数、schema 違反 |
| Thumbnail | YMM4 サムネ slot patch | `audit-thumbnail` 結果、`thumbnail_patch_input` 編集補助、`patch-thumbnail` 実行結果と readback |
| Settings | ローカル設定 | `config/nlmytgen_path.json` の存在確認、NLMYTGen bridge readiness |

Editing タブの action form は **ED-01 / ED-02a の手動 cut 入力範囲だけ** GUI に出す。ED-02 `generate-cuts` と ED-04 `generate-subtitles` は CLI 実装済みだが、GUI button はまだ置かない。文脈チェック（ED-03）／ NLE export（ED-06）は未実装なので GUI 上に表示しない。

Publishing は未実装なのでタブとして置かない。FEATURE_REGISTRY の `PB-*` / `INT-01` が実装される段階で再評価する。

## 画面原則

- 最初の画面は dashboard / operator console。landing page は作らない。
- 4レーンの状態を「done / blocked / missing / manual needed」で表示する。
- エラーは stack trace ではなく、対象 artifact、原因、次の操作を並べる。
- readback は必ず独立セクションで表示する。特に `patch-thumbnail` は rights readback、material validation、NLMYTGen audit、patch、readback の段を分ける。
- 未実装 action は disabled button として置かない。MVP では upload / fetch / bg-removal API は実行導線を持たない。

## Backend 境界

- GUI は Python pipeline を再実装しない。
- MVP では CLI subprocess または薄い local wrapper 経由で既存コマンドを呼ぶ。
- GUI の保存対象は、既存 JSON artifact と local config のみ。
- tokens、OAuth secrets、実素材、episode 作業物は `.gitignore` 境界に従い、repo に含めない。

## SH-02-lite: Episode Status Adapter

GUI 実装前に、最小の status adapter を置く。これは full `episode_pack` ではなく、既存 artifact を読み取って GUI が必要な状態を返す薄い shared infra とする。

含めるもの:

- episode id
- artifact existence: rights / ledger / thumbnail input / thumbnail result
- compliance status
- material count and audit issues count
- thumbnail patch stage status
- next recommended action

含めないもの:

- `edit_pack`
- `publish_draft`
- `upload_receipt`
- NLMYTGen と物理共有する manifest

full `episode_pack` は Editing / Publishing が実装されてから再評価する。

CLI:

```bash
python -m src.cli.main status-episode \
  --episode-dir samples/episode_example \
  --format json
```

## Acceptance

- `npm` / Electron dev server で GUI が起動する。
- Episode / Rights / Materials / Thumbnail / Settings の MVP タブが表示される。
- 少なくとも sample episode を読み、missing / blocked / ready の状態が破綻なく表示される。
- 既存 Python tests は引き続き pass。GUI 側のテストは smoke 1-2 件に留める。
- 外部 API 呼び出し、YouTube upload、元動画ダウンロード、背景切り抜き API 呼び出しは未実装のため発生しない。

## NLMYTGen への逆提案メモ

GUI 実装で有効だった知見は、NLMYTGen 側へ doc / issue ベースで提案できる。ただし NLMYTGen 側ファイルは直接編集しない。

候補:

- lane / readback 状態表示
- readback の段階表示
- local config readiness 表示
- manual-needed step の明示
