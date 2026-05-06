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

- **current_lane**: Slice 2 (c) GUI Phase 1 done、Phase 2 (SH-03b) は別スライスで承認待ち
- **current_slice**: Slice 2 — SH-02L / SH-03 done。次は (a) Editing core 着手 か SH-03b GUI Phase 2 かを user が選ぶ
- **next_action（assistant 側）**: ユーザーから方向指示を受けるまで idle。判断材料は `docs/RUNTIME_STATE.md` 「次に変えうる判断」と FEATURE_REGISTRY 内の proposed 候補（ED-01..06 / PB-01..04 / SH-03b / SH-04）
- **next_action（user 側）**: 並行で SLICE1_WALKTHROUGH.md を辿り、YMM4 thumbnail base template の authoring と end-to-end の `patch-thumbnail` 実走。完了後 GUI Phase 1 でも結果を確認できる。

### Slice 2 (c) Phase 1 done（SH-03: GUI MVP read-only console）

- `gui/` Electron skeleton — `package.json`（Electron `^30`）/ `main/index.js`（IPC `repoRoot` `listEpisodes` `getStatus` `revealPath`）/ `preload/index.js`（contextBridge）/ `renderer/{index.html,styles.css,index.js}`
- 5 タブ MVP — Episode（dashboard table）/ Rights / Materials / Thumbnail（readback table 含む）/ Settings（bridge readiness）
- `status-episode` JSON を spawn 経由で取得（cwd=リポ root）。Python は PATH または `CLIPPIPE_PYTHON` で指定
- `docs/GUI_CONVENTIONS.md` — 整合-A 規約（配色・状態語彙・タブ命名・readback 表示・危険操作・逆提案運用）
- Phase 2 = action 導線は **SH-03b** として proposed に分離。実行系 button は Phase 1 で意図的に出さない
- 既存 Python tests 34 件は変更なし。GUI 側 smoke は Electron 起動を伴うため、後続スライスで Playwright/jest 系を入れるか判断
- セキュリティ: `contextIsolation: true` / `nodeIntegration: false` / `sandbox: true` / 厳格 CSP（`default-src 'self'; script-src 'self'`）

### Slice 2 (d) done（TH-W01: Slice 1 walkthrough 補助）

- `docs/walkthrough/YMM4_THUMBNAIL_TEMPLATE_AUTHORING.md` — YMM4 上で `thumb.text.*` / `thumb.image.*` の Remark 規約を持つ base template を作る手順、トラブルシューティング、命名規約 (`^thumb\.(text|image|color|transform)\.[a-z0-9_]+$`)
- `docs/walkthrough/SLICE1_WALKTHROUGH.md` — `init-episode` から `patch-thumbnail` までの 11 ステップ runbook、各段 fail パターンとリトライ手順
- `samples/episode_example/{rights_manifest.json,material_ledger.json,thumbnail_patch_input.json}` と `samples/episode_example/materials/mat_001/sidecar.json` — illustrative example。**実素材は同梱しない**（第三者素材 repo 同梱の禁止）
- 既存テスト 31 件は変更なし。docs only commit。

### Slice 2 (c) approved → done（履歴）

- `docs/GUI_MVP_SCOPE.md` — Electron 採用、MVP タブ（Episode / Rights / Materials / Thumbnail / Settings）、SH-02-lite episode status adapter、dangerous operation exclusion を固定。
- GUI は NLMYTGen とアプリ共有しない。見た目・操作感・タブ構造・readback 表示パターンだけ揃える。
- MVP は Slice 1 artifact の操作面に限定し、Editing / Publishing は表示しない。
- Phase 1 実装は本ブロックで完了（上記 Phase 1 done セクション参照）。Phase 2 は SH-03b に分離。

### Slice 2 (c) done（SH-02L: episode status adapter）

- `src/pipeline/episode_status.py` — `rights_manifest` / `material_ledger` / `thumbnail_patch_input` / `thumbnail_patch_result` の存在、gate 状態、bridge config readiness、next_action を集約。
- `src/cli/status_episode.py` — `status-episode --episode-dir ... --format json|text` を追加。
- `tests/test_episode_status.py` — 3 tests。累計 34 tests passing。
- full `episode_pack` は Editing / Publishing 実装後に再評価。

### Slice 2 (c) in progress（SH-03: Electron GUI MVP skeleton）

- `package.json` — Electron 42.0.0（2026-05-07 時点の npm registry 現行）を dev dependency として定義。
- `gui/` — Electron main/preload/renderer/CSS/smoke を追加。
- MVP は `status-episode` を IPC 経由で呼び、Episode / Rights / Materials / Thumbnail / Settings の状態を表示する。
- GUI から upload / fetch / bg-removal API は実行しない。

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
