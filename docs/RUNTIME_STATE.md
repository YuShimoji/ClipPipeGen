# Runtime State — ClipPipeGen

ブロックの主成果と次の手を更新する。compact 後の再アンカリングではこのファイルを読む。

## 現在位置

### Slice 1.3 done（TH-01 / SH-01: NLMYTGen bridge + thumbnail patch orchestrator）

- Slice 1 ソフトウェア実装は **6/6 done**（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）
- 累計テスト 31 件 all passing。NLMYTGen subprocess は monkeypatch でモック。
- **実装内容**：
  - `src/pipeline/nlmytgen_bridge.py` — `BridgeConfig.load` / `call_nlmytgen` (silent fallback 禁止) / `audit_thumbnail_template` / `patch_thumbnail_template`
  - `src/pipeline/thumbnail_patch.py` — TH-01 5 段検証オーケストレータ：(1) compliance gate (2) material validation (3) NLMYTGen audit (4) NLMYTGen patch (5) readback
  - `src/cli/{audit_thumbnail,patch_thumbnail}.py`
  - `config/nlmytgen_path.json.example`（本体は `.gitignore` 対象）
  - `tests/test_thumbnail_patch.py` — 8 件（bridge 3 + orchestrator 4 + input validator 1）
- **保留中**：実 YMM4 base template `.ymmp`（`thumb.text.*` / `thumb.image.*` Remark 設定済み）に対する end-to-end walkthrough。これは user-owned acceptance step として `FIRST_SLICE.md` DoR に既に記載されている。テンプレ authoring は人手作業のため、ソフト側の DoD は閉じてよい。

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

- **current_lane**: Slice 2 (c) GUI MVP（SH-03）着手
- **current_slice**: Slice 2 — (d) walkthrough 補助 done、(c) GUI 最小は approved
- **next_action（assistant 側）**: `docs/GUI_MVP_SCOPE.md` に従い、SH-02-lite episode status adapter と Electron GUI MVP skeleton を実装する。外部 API / upload / asset fetch / bg-removal API は触らない。
- **next_action（user 側）**: 並行で SLICE1_WALKTHROUGH.md を辿り、YMM4 thumbnail base template の authoring と end-to-end の `patch-thumbnail` 実走。所要は YMM4 authoring 30〜60 分 + CLI 実行 5〜10 分。

### Slice 2 (d) done（TH-W01: Slice 1 walkthrough 補助）

- `docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md` — YMM4 上で `thumb.text.*` / `thumb.image.*` の Remark 規約を持つ base template を作る手順、トラブルシューティング、命名規約 (`^thumb\.(text|image|color|transform)\.[a-z0-9_]+$`)
- `docs/walkthrough/SLICE1_WALKTHROUGH.md` — `init-episode` から `patch-thumbnail` までの 11 ステップ runbook、各段 fail パターンとリトライ手順
- `samples/episode_example/{rights_manifest.json,material_ledger.json,thumbnail_patch_input.json}` と `samples/episode_example/materials/mat_001/sidecar.json` — illustrative example。**実素材は同梱しない**（第三者素材 repo 同梱の禁止）
- 既存テスト 31 件は変更なし。docs only commit。

### Slice 2 (c) approved（SH-03: GUI MVP）

- `docs/GUI_MVP_SCOPE.md` — Electron 採用、MVP タブ（Episode / Rights / Materials / Thumbnail / Settings）、SH-02-lite episode status adapter、dangerous operation exclusion を固定。
- GUI は NLMYTGen とアプリ共有しない。見た目・操作感・タブ構造・readback 表示パターンだけ揃える。
- MVP は Slice 1 artifact の操作面に限定し、Editing / Publishing は表示しない。
- 次ブロックで実装着手する。

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
- GUI MVP: [GUI_MVP_SCOPE.md](GUI_MVP_SCOPE.md)
- 不変条件: [INVARIANTS.md](INVARIANTS.md)
- 自動化境界: [AUTOMATION_BOUNDARY.md](AUTOMATION_BOUNDARY.md)
- レーン責務: [LANES.md](LANES.md)
- 機能一覧: [FEATURE_REGISTRY.md](FEATURE_REGISTRY.md)
- 現スライス: [FIRST_SLICE.md](FIRST_SLICE.md)
- schema: [SCHEMAS/v1/](SCHEMAS/v1/)
