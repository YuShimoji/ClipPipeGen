# samples/episode_example/

Slice 1 + Editing 雛形の **runnable example**。CLI / GUI で開いた瞬間に実体が読める状態。実権利物は同梱しない。

## 構成

| ファイル | 状態 | 用途 |
|---|---|---|
| `rights_manifest.json` | ✅ runnable（compliance_check.status=passed） | 権利確認 manifest 雛形 |
| `material_ledger.json` | ✅ runnable（hash 一致） | 1 素材登録済み ledger |
| `materials/mat_001/sidecar.json` | ✅ runnable（hash 一致） | 出典・利用条件 sidecar |
| `materials/mat_001/x.png` | ✅ runnable（64×64 RGBA placeholder） | サムネ用人物画像のスタブ。半透明マゼンタ。**本物の人物画像に差し替えて使う前提** |
| `edit_pack.json` | ✅ runnable（cut_001 selected） | Editing レーン雛形 |
| `thumbnail_patch_input.json` | ✅ runnable（schema valid） | YMM4 サムネ slot patch 入力例 |
| `templates/thumbnail/base.ymmp` | ❌ **要 user authoring** | YMM4 で `thumb.text.*` / `thumb.image.*` Remark 設定済みの base ymmp |

## どこまで動くか

リポ root から：

```bash
python -m src.cli.main status-episode --episode-dir samples/episode_example --format text
```

出力（期待値）:

```
episode: episode_example
dir: samples/episode_example
rights: ready (passed)
materials: ready (1 materials)
editing: ready (1 cuts)
thumbnail: ready (3 slots)
next[assistant]: Run patch-thumbnail after YMM4 base template is ready
```

つまり Slice 1 walkthrough のうち **ステップ 1〜9 はサンプルだけで動く**。10（patch-thumbnail）は YMM4 base template が要るので user authoring 待ち。

GUI で見る場合：

```bash
npm install
npm start
```

Episode dir input は `samples/episode_example` がデフォルト。Episode タブにレーン状態が表示される。

## 含まないもの（INVARIANTS / 権利配慮）

| 必要物 | 配置場所 | 備考 |
|---|---|---|
| 実本物のキャラクター画像 / 元動画 | repo に **同梱しない** | 第三者素材は repo に置かない（INVARIANTS）。`materials/mat_001/x.png` は placeholder 形状のみ |
| YMM4 base template `.ymmp` | `samples/episode_example/templates/thumbnail/base.ymmp`（任意の場所に置いて `thumbnail_patch_input.base_template.ymmp_path` を書き換えてもよい） | `.ymmp` ゼロ生成禁止のため、YMM4 上で人手 authoring。手順は [`docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md`](../../docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) |
| `config/nlmytgen_path.json` | リポ root の `config/`（gitignored） | NLMYTGen の checkout パス。例: `config/nlmytgen_path.json.example` をコピー＋編集 |

## Production への昇格

このサンプルは **そのまま投稿対象にしない**。実 episode を作る時：

1. `python -m src.cli.main init-episode --episode-id ep_<your_id> --root episodes`
2. `episodes/ep_<your_id>/rights_manifest.json` を本物の URL / talent / 出典で書き換える
3. 本物の素材（権利確認済）を `materials/<id>/` に置き、sidecar を書く
4. `register-material`, `init-edit-pack`, `add-cut-candidate` を実 ID に対して実行
5. `thumbnail_patch_input.json` を実 episode 用に作成
6. YMM4 base template を authoring
7. `patch-thumbnail` を実走

サンプルは常にこの道筋を「形だけ動かして見せる」役割に徹する。

## 注意

- `rights_manifest.source_video.url` の URL はプレースホルダー（`PLACEHOLDER_REPLACE_ME`）。実走時には実 URL に差し替えること。
- `materials/mat_001/x.png` は 64×64 半透明マゼンタの placeholder。サムネ目視確認用ではない。
- `edit_pack.cut_candidates[].reason` も illustrative。実 cut 判断の根拠は user 側で書く。
