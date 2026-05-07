# Slice 1 Walkthrough — 1 episode の最小実証

`init-episode` から `patch-thumbnail` までを通す happy path。終わると、YMM4 で開ける slot patch 済み `.ymmp` が手に入る。

## Quickstart（サンプルだけで動く範囲）

リポ root で次の 2 コマンドだけ：

```bash
python -m src.cli.main status-episode --episode-dir samples/episode_example --format text
```

これで `samples/episode_example/` 内の `rights / materials / editing / thumbnail` 4 レーンの状態が表示される。`next[assistant]: Run patch-thumbnail after YMM4 base template is ready` まで進めば、CLI 側のチェーンは閉じている。

GUI で見るなら：

```bash
npm install
npm start
```

Episode タブに同じ状態が出る。後はステップ 8（YMM4 base template authoring）以降を実エピソードで進める。

サンプルの内訳と「なにが含まれていないか」は [`samples/episode_example/README.md`](../../samples/episode_example/README.md)。

## 前提

| 項目 | 確認方法 |
|---|---|
| Python 3.10+ | `python --version` |
| ClipPipeGen のローカル checkout | `cd <ClipPipeGen>` できる |
| NLMYTGen のローカル checkout | `<NLMYTGen>/src/cli/main.py` が存在する |
| `config/nlmytgen_path.json`（gitignored） | 後述の手順で作成 |
| YMM4 base template `.ymmp`（`thumb.*` Remark 設定済み） | [YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md](YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) を参照 |
| 透過PNG（人物画像）1枚 | 外部 bg-removal で生成済み |

## 全体フロー

```
[人手] YMM4 で thumbnail base template を authoring
   ↓
[CLI] init-episode             → rights_manifest skeleton
[人手] rights_manifest を埋める（source_video / talents / disclosures）
[CLI] validate-rights          → schema check
[CLI] set-compliance --status passed --checked-by user:<you>
   ↓
[人手] 透過PNG を materials/<id>/ に配置
[人手] sidecar.json を書く（出典・ライセンス・利用条件）
[CLI] register-material        → ledger に追加 (sidecar 必須・hash・PNG 透過チェック)
[CLI] audit-material-ledger    → 整合性確認
   ↓
[CLI] audit-thumbnail          → NLMYTGen bridge で slot 存在確認
[人手] thumbnail_patch_input.json を書く
[CLI] patch-thumbnail          → 5段検証＋NLMYTGen patch＋readback
   ↓
[人手] patched .ymmp を YMM4 で開いて構図確認・微調整・PNG 書き出し
```

## ステップ詳細

### 0. 環境セットアップ（初回のみ）

```bash
# NLMYTGen path 設定
cp config/nlmytgen_path.json.example config/nlmytgen_path.json
# config/nlmytgen_path.json を開いて nlmytgen_root を実環境のパスに書き換える
```

`config/nlmytgen_path.json` は `.gitignore` 対象。コミットしないこと。

### 1. episode 初期化

```bash
python -m src.cli.main init-episode \
  --episode-id ep_20260507_hololive_<short_label> \
  --root episodes
```

`episodes/ep_20260507_hololive_<short_label>/rights_manifest.json` が `compliance_check.status=pending` で生成される。

### 2. rights_manifest を埋める

エディタで `episodes/<episode_id>/rights_manifest.json` を開いて以下を記入：

- `source_video.url` / `title` / `channel` / `channel_id` / `vod_status`
- `talents[]`（`agency=hololive` / `guideline_url` は公式ドメイン必須）
- `third_party_ip[]`（ゲーム・楽曲が混入するなら、各項目の `permitted` を確認）
- `required_disclosures[]`（最低 `source_link` と `rights_credit`）
- `publication_constraints`

雛形は [`samples/episode_example/rights_manifest.json`](../../samples/episode_example/rights_manifest.json) を参照。

### 3. 構造 validate

```bash
python -m src.cli.main validate-rights \
  --rights-manifest episodes/<episode_id>/rights_manifest.json \
  --format text
```

`schema: OK` と `compliance: passable` の両方が出れば次へ。

### 4. compliance を passed にする

```bash
python -m src.cli.main set-compliance \
  --rights-manifest episodes/<episode_id>/rights_manifest.json \
  --status passed \
  --checked-by user:<your_name>
```

成功すると `compliance_check.status=passed`、`checked_at` / `checked_by` が記録される。

**review note として残る典型例**（local CLI を止めない）：

| code | 原因 |
|---|---|
| `VOD_STATUS_REVIEW` | `source_video.vod_status` が `private` / `members_only` / `deleted` |
| `THIRD_PARTY_IP_REVIEW` | `third_party_ip[]` のどれかが `permitted=false` |

これらは `compliance_check.warnings[]` に書き戻され、後段 CLI / GUI で readback として表示される。

### 5. 素材を配置

例：透過PNG を `materials/mat_001/x.png` に配置。

`materials/mat_001/sidecar.json` を作成（[`samples/episode_example/materials/mat_001/sidecar.json`](../../samples/episode_example/materials/mat_001/sidecar.json) を参照）。

`asset_hash_sha256` は実ファイルの SHA256 と一致させる必要がある：

```bash
# Windows / WSL
python -c "import hashlib;print(hashlib.sha256(open('materials/mat_001/x.png','rb').read()).hexdigest())"
# 出力された hex を sidecar.json の asset_hash_sha256 に貼る
```

### 6. ledger に登録

```bash
python -m src.cli.main register-material \
  --episode-id <episode_id> \
  --kind character_image \
  --subkind transparent_png \
  --file materials/mat_001/x.png \
  --sidecar materials/mat_001/sidecar.json \
  --intended-use thumbnail \
  --registered-by user:<your_name>
```

成功すると `episodes/<episode_id>/material_ledger.json` に entry が追加される。

**fail する典型例**：

| エラー | 原因 |
|---|---|
| `sidecar asset_hash_sha256 does not match file` | sidecar の hash と実ファイルが食い違う |
| `transparent_png but PNG color_type is not 4/6` | `subkind=transparent_png` を指定したが PNG が RGBA じゃない |
| `sidecar invalid: SIDECAR_USAGE_CONDITIONS_EMPTY` | `usage_conditions[]` が空（最低 1 つ必須） |

### 7. ledger 監査

```bash
python -m src.cli.main audit-material-ledger \
  --episode-id <episode_id> \
  --format text
```

`OK (1 materials)` を確認。

### 8. base template を audit

事前に YMM4 で authoring 済みの base template に対して slot 検出：

```bash
python -m src.cli.main audit-thumbnail \
  --base-template templates/thumbnail/base.ymmp \
  --format json
```

期待される `slots[]` がすべて出ていることを確認。`THUMB_TEMPLATE_NO_SLOTS` 等が出た場合は [YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md](YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md) のトラブルシューティングを参照。

### 9. thumbnail_patch_input.json を書く

雛形は [`samples/episode_example/thumbnail_patch_input.json`](../../samples/episode_example/thumbnail_patch_input.json)。

最低限差し替える項目：

- `episode_id` — 自分の episode_id
- `rights_manifest_path` / `material_ledger_path` — 自分の episode の絶対 or 相対パス
- `base_template.ymmp_path` — 8 で audit した base
- `slots[].value`（テキスト系）と `slots[].source_material_id`（画像系）
- `output.ymmp_path` — 書き出し先

### 10. patch 実行

```bash
python -m src.cli.main patch-thumbnail \
  --input episodes/<episode_id>/thumbnail_patch_input.json \
  --output-result episodes/<episode_id>/thumbnail_patch_result.json
```

5 段検証：

1. **rights readback** — `rights_manifest.compliance_check.status` を結果に記録するが、値だけでは fail しない
2. **material validation** — 各 image slot の material / sidecar / file path を解決する。source/license/restriction は metadata として保持する
3. **NLMYTGen audit** — base template に該当 slot がなければ `BRIDGE_AUDIT_MISSING_SLOTS`
4. **NLMYTGen patch** — `audit-thumbnail-template` 経由で slot 差し替え
5. **readback** — patched ymmp の各 slot 値が input と一致するか確認

成功すると `output.ymmp_path` に patched ymmp が書かれる。

### 11. YMM4 で目視確認・最終調整・書き出し

YMM4 で patched ymmp を開いて：

- 文字・画像が想定 slot に入っているか目視確認
- 構図・色味の微調整（人手判断、INVARIANTS）
- 静止画として書き出し（YMM4 の機能）

ここまで終われば Slice 1 walkthrough は完了。書き出した PNG は YouTube 投稿時のサムネとして使える。

## 失敗時のリトライ

各段の `errors[]` を読む：

- `RIGHTS_MANIFEST_NOT_FOUND` — `rights_manifest.json` の path を見直す
- `MATERIAL_VALIDATION_FAILED` — `material_validation.violations[]` の `reason` を読み、sidecar を直して `register-material` を再実行（または別素材に切り替え）
- `BRIDGE_AUDIT_*` — base template の `Remark` 設定を見直す
- `BRIDGE_PATCH_FAILED` — `patch_result.bridge_error` と `stderr_tail` を読む
- `READBACK_MISMATCH` — NLMYTGen 側の patch 動作と本リポの期待値が食い違っている可能性。`thumbnail_patch_result.json` の `applied_slots[]` を見て slot ごとの一致状況を確認

## 次のステップ

Slice 1 walkthrough が成功したら：

- 同じ手順で別 episode を試す（再現性確認）
- Slice 2（GUI / Editing core / Publishing）へ進む（[RUNTIME_STATE.md](../RUNTIME_STATE.md) の `next_action`）
