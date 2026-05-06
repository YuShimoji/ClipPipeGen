# Runtime State — ClipPipeGen

ブロックの主成果と次の手を更新する。compact 後の再アンカリングではこのファイルを読む。

## 現在位置

### Slice 1.2 done（MS-01 / MS-02 / MS-03: material_ledger + sidecar + 透過PNG 受け入れ）

- Bootstrap commit `d5efd86`、CR-01 commit `5be5439`、Slice 1.2 commit は本ブロック内
- Slice 1 done 状態: `CR-01 / MS-01 / MS-02 / MS-03` (4/6)。残り `TH-01` / `SH-01` は Slice 1.3 で実装
- **Slice 1.2 実装内容**：
  - `src/pipeline/validation.py` — 共有 `ValidationIssue`（CR-01 の dataclass を抽出）
  - `src/pipeline/material_sidecar.py` — schema validator / `assert_usable_for_thumbnail` gate / `restrictions_are_at_least_as_strict`（derived_from 厳格度継承）
  - `src/pipeline/material_ledger.py` — `build_skeleton` / `register_material` / `audit_ledger` / `is_transparent_png` (MS-03) / `assert_thumbnail_usable` gate
  - `src/cli/{register_material,audit_material_ledger}.py`
  - `tests/test_material_sidecar.py` — 6 tests（positive 1 + critical negatives 5）
  - `tests/test_material_ledger.py` — 8 tests（PNG 判定 2 + register 3 + audit 2 + CLI smoke 1）
- 累計テスト: 23 件 all passing
- gate enforcement 確認済：
  - sidecar の `source.kind=unverified` / `license.kind in {unknown,fair_use_claimed}` / `restrictions.thumbnail_use=denied` で `assert_usable_for_thumbnail` が `SidecarUsageError`
  - `register-material` で sidecar hash 不一致 / 透過PNG 宣言 vs 実 RGB の不整合 / sidecar 構造違反は `LedgerError`
  - `audit-material-ledger` で hash mismatch / `intended_uses=thumbnail` ＋ thumbnail-blocked sidecar の組み合わせを検出

### project

- name: ClipPipeGen
- repo: https://github.com/YuShimoji/ClipPipeGen
- 並列ローカルパス: `c:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`
- 関連リポ: [NLMYTGen](https://github.com/YuShimoji/NLMYTGen)（CLI subprocess 経由でのみ再利用）

### lane / slice

- **current_lane**: Thumbnail
- **current_slice**: Slice 1 — Material Sourcing + Thumbnail 最小実証（[FIRST_SLICE.md](FIRST_SLICE.md)）
- **current_sub_slice**: Slice 1.3 — TH-01 + SH-01（NLMYTGen `audit-thumbnail-template` / `patch-thumbnail-template` の CLI bridge と、`config/nlmytgen_path.json` 経由の subprocess wrapper）
- **next_action**: NLMYTGen 側の正確な CLI コマンド名・引数仕様を `docs/dev/CLI_REFERENCE.md` で読み取り（read-only、配置問題なし）、`src/pipeline/nlmytgen_bridge.py` と `src/cli/{audit_thumbnail,patch_thumbnail}.py` を実装。実 NLMYTGen subprocess の初回呼び出し時のみユーザーへ通知する。

## 主成果物

- active_artifact: Slice 1 minimum proof（rights_manifest → 透過PNG＋sidecar → YMM4 サムネ slot patch → readback）
- artifact_surface: CLI（`src/cli/*`）→ JSON manifest → patched `.ymmp` → 人手で YMM4 確認・書き出し
- last_change_relation: リポ初期化（v0）

## カウンター

- blocks_since_user_visible_change: 0
- slices_completed: 0

## 次に変えうる判断

- Slice 1 完了後、Slice 2 で **Editing core 着手** か **Publishing integration 着手** かを判断する
- NLMYTGen CLI bridge が想定通り動作した場合、shared package 化を検討（ただし CLI bridge で 2-3 個の実例が出てから）
- ホロライブ以外の VTuber 事務所（にじさんじ等）への対象拡大は v1 では検討しない。Slice 1 完了後に rights_manifest 構造の汎用性を見て判断する

## 関連ドキュメント

- 入口: [README.md](../README.md) / [AGENTS.md](../AGENTS.md)
- 方針: [CLAUDE.md](../CLAUDE.md)（ルート）
- 不変条件: [INVARIANTS.md](INVARIANTS.md)
- 自動化境界: [AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- レーン責務: [LANES.md](LANES.md)
- 機能一覧: [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- 現スライス: [FIRST_SLICE.md](FIRST_SLICE.md)
- schema: [SCHEMAS/v1/](SCHEMAS/v1/)
