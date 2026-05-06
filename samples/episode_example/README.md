# samples/episode_example/

Slice 1 の walkthrough で参照する **illustrative example**。実データではない。

## 含むもの

| ファイル | 用途 |
|---|---|
| `rights_manifest.json` | 1 episode の権利確認 manifest 雛形（compliance_check.status=passed の状態） |
| `material_ledger.json` | 1 素材だけ登録済みの ledger 例 |
| `materials/mat_001/sidecar.json` | 1 素材の出典・利用条件 sidecar 例 |
| `thumbnail_patch_input.json` | YMM4 base template への slot patch 入力例 |

## 含まないもの（ユーザー側で用意する）

| 必要物 | 配置場所 | 備考 |
|---|---|---|
| 透過PNG（人物画像） | `samples/episode_example/materials/mat_001/x.png`（または任意のパスに置いて sidecar / ledger を書き換え） | 背景切り抜き済み RGBA PNG。本リポは生成しない（INVARIANTS） |
| YMM4 base template `.ymmp` | `samples/episode_example/templates/thumbnail/base.ymmp`（または任意） | `thumb.text.*` / `thumb.image.*` の Remark 設定済み。authoring 手順は [`docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md`](../../docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) |
| `config/nlmytgen_path.json` | リポ root の `config/`（gitignored） | NLMYTGen の checkout パス。例: `config/nlmytgen_path.json.example` をコピー＋編集 |

## 使い方

[`docs/walkthrough/SLICE1_WALKTHROUGH.md`](../../docs/walkthrough/SLICE1_WALKTHROUGH.md) を参照。本ディレクトリの JSON は walkthrough 中で `--input` などに指定する元データとして使う。

## 注意

- `rights_manifest.source_video.url` の URL はプレースホルダー。実走時は実際の動画 URL に差し替え、ホロライブ二次創作ガイドラインや各タレント個別方針と照合した上で `compliance_check` を確定すること。
- sidecar の `attribution_text` も例示。実運用時は YouTube 概要欄に転記できる正確な文字列にする。
- 本ディレクトリ内に **実際のキャラクター画像・元動画ファイル** は同梱しない。第三者素材の repo 同梱は避ける。
