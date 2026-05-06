# YMM4 Thumbnail Template Authoring

`patch-thumbnail` で slot 差し替え可能な base template `.ymmp` を YMM4 で authoring する手順。**ここは人手作業で、ClipPipeGen の責務外**（INVARIANTS：YMM4 上の構図・配色・配置は人手判断）。本ドキュメントはそのための実務手順をまとめたもの。

## 前提

- YMM4 がインストールされ、起動できる
- 切り抜き動画用のサムネイルデザイン（構図・配色・テキスト位置）が決まっている、または雛形として用意したい
- 透過PNG（人物画像）と背景画像が手元にある（または後でプレースホルダーから差し替える）

## 完成形

YMM4 で開いたとき、以下を満たす `.ymmp`：

- キャンバスサイズが YouTube サムネイル比率（推奨 1280×720）
- メインタイトル文字（TextItem）が配置され、`Remark` フィールドに `thumb.text.title` が設定されている
- サブタイトル文字（TextItem）が配置され、`Remark` に `thumb.text.subtitle` が設定されている（任意）
- キャラ画像（ImageItem）が配置され、`Remark` に `thumb.image.character` が設定されている
- 背景画像（ImageItem）が配置され、`Remark` に `thumb.image.background` が設定されている（任意）
- 配置・サイズ・色は **人間が決めた構図** で固定されている（slot patch で差し替えるのは中身だけで、構図は変えない）

## 手順

### 1. プロジェクト新規作成

1. YMM4 を起動
2. ファイル → 新規プロジェクト
3. 解像度を 1280×720 に設定（YouTube サムネ推奨）
4. fps はサムネ用なので何でもよい（30 で OK）

### 2. 背景の配置（任意）

サムネに背景画像を入れる場合：

1. プロジェクトに `samples/episode_example/materials/mat_002/bg.png` 等の背景画像を追加
   - **本物のサムネ用素材は repo にコミットしない**（INVARIANTS / .gitignore に `materials/` あり）
   - 雛形 authoring 中はダミー画像（単色 PNG など）でよい
2. ImageItem としてタイムラインに配置し、画面全体を覆うように調整
3. **ImageItem を選択 → プロパティパネルの `Remark` フィールドに `thumb.image.background` を入力**

### 3. キャラ画像の配置

1. 透過PNG のキャラ画像を追加
   - 雛形 authoring 中はダミー透過PNG でよい
2. ImageItem としてタイムラインに配置
3. 画面の右側 1/3 などサムネとしての構図位置に配置・拡縮
4. **ImageItem を選択 → `Remark` に `thumb.image.character` を入力**

### 4. メインタイトルテキストの配置

1. TextItem を新規追加
2. プレースホルダー文字を入力（例: `タイトル候補`）
3. フォント・サイズ・色を決める。サムネの可読性は **配信プレイヤー上の小サイズ表示** に耐える太さが基本
4. 画面上の位置を調整（左寄せが多い）
5. **TextItem を選択 → `Remark` に `thumb.text.title` を入力**

### 5. サブタイトルやハッシュタグ等の追加（任意）

同様に TextItem を追加して `Remark` に以下を設定：

- `thumb.text.subtitle` — 副題、ハッシュタグ等
- `thumb.text.tag` — 分類タグ等
- 必要に応じて任意の `thumb.text.<id>` を追加（id は `[a-z0-9_]+` のみ）

### 6. 名前付け規約

`Remark` 値は以下の正規表現に合致する必要がある（patch-thumbnail がここで弾く）：

```
^thumb\.(text|image|color|transform)\.[a-z0-9_]+$
```

- `text` — TextItem の文字本文を差し替える slot
- `image` — ImageItem の `FilePath` を差し替える slot
- `color` — テキスト色や背景色を差し替える slot（YMM4 側のサポート範囲に依存）
- `transform` — X/Y/Zoom/Rotation を差し替える slot

OK 例: `thumb.text.title` / `thumb.image.character` / `thumb.text.episode_number_01`
NG 例: `thumb.text.Title` （大文字）/ `thumb.image.メイン` （非ASCII）/ `title` （prefix なし）

### 7. 保存

`samples/episode_example/templates/thumbnail/base.ymmp` などに保存。

> **注意**: `samples/` 配下に置く場合は `.gitignore` の対象範囲を確認。雛形を **そのままリポジトリにコミット** したい場合は、第三者素材を含まないこと（プレースホルダー画像のみで構成する）。

### 8. 検証

```bash
# slot が正しく検出されるか確認
python -m src.cli.main audit-thumbnail \
  --base-template samples/episode_example/templates/thumbnail/base.ymmp \
  --format json
```

期待出力（slot 数とそれぞれの kind/id が並ぶ JSON）：

```json
{
  "slot_count": 4,
  "slots": [
    {"kind": "image", "id": "background", ...},
    {"kind": "image", "id": "character", ...},
    {"kind": "text",  "id": "title", ...},
    {"kind": "text",  "id": "subtitle", ...}
  ],
  "errors": []
}
```

`errors` に `THUMB_TEMPLATE_NO_SLOTS` や `THUMB_TEXT_SLOT_NO_TEXT_FIELD` などが出る場合は YMM4 上の `Remark` 設定を見直す。

## トラブルシューティング

| 症状 | 原因の候補 | 対処 |
|---|---|---|
| `THUMB_TEMPLATE_NO_SLOTS` | TextItem / ImageItem に `Remark` が設定されていない、または `thumb.` で始まっていない | 全 slot 候補に Remark を付け直す |
| `THUMB_TEXT_SLOT_NO_TEXT_FIELD` | TextItem ではないアイテムに `thumb.text.*` を付けた | TextItem 限定にする |
| `THUMB_IMAGE_SLOT_NOT_IMAGE_ITEM` | ImageItem ではないアイテムに `thumb.image.*` を付けた | ImageItem 限定にする |
| `THUMB_IMAGE_SLOT_NO_FILEPATH` | ImageItem に元画像が設定されていない | ImageItem に何かしらの画像を割り当てる |
| `THUMB_GEOMETRY_ROUTE_MISSING` | `thumb.transform.*` を付けたが該当 transform フィールドが項目に存在しない | YMM4 側で X/Y/Zoom/Rotation を一度設定する |

## やらないこと

INVARIANTS / AUTOMATION_BOUNDARY に従い、本ガイドは以下をカバーしない：

- 構図・配色・最終クリック感の決定（人手判断）
- 透過PNG の自動生成（外部前処理として受け取る）
- ymmp のゼロからの生成（必ず YMM4 で human authoring）
- サムネイルテンプレを Python から作成・編集（slot patch のみ許可、authoring は YMM4）

## 関連

- [SLICE1_WALKTHROUGH.md](SLICE1_WALKTHROUGH.md) — episode 単位の通し手順
- [docs/SCHEMAS/v1/thumbnail_patch_input.md](../SCHEMAS/v1/thumbnail_patch_input.md) — patch-thumbnail に渡す入力 schema
- NLMYTGen 側 audit/patch CLI 仕様: NLMYTGen の `audit-thumbnail-template` / `patch-thumbnail-template`
