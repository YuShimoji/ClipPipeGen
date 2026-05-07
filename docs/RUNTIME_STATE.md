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

- **current_lane**: Slice 2 — SH-04 done / SH-03b done / ED-01 / ED-02a done（外部レーン）
- **current_slice**: Slice 2 — 主要承認済 ID は出尽くした。次の意思決定は (i) SH-03b に edit_pack 操作（init-edit-pack / add-cut-candidate）を GUI 統合する Phase 2.5、(ii) ED-02 本体（音声・字幕ベース自動 cut 候補、speech-to-text 候補選定が要る）、(iii) PB / INT 着手のいずれか
- **next_action（assistant 側）**: 上記 (i)〜(iii) の方向はユーザーの優先順次第。idle until directed。低危険・前進値ありで言えば (i) edit_pack の GUI 統合（既存 SH-03b の延長で UI/IPC 追加するだけ）が最小コスト
- **next_action（user 側）**: 並行で SLICE1_WALKTHROUGH.md を辿り、YMM4 thumbnail base template の authoring と end-to-end の `patch-thumbnail` 実走。SH-03b で GUI から実行可能になったので、CLI 直叩きより楽になっている

### Slice 2 (c) Phase 2 done（SH-03b: GUI action 導線）

- `gui/main.cjs` — IPC `action:setCompliance` / `action:registerMaterial` / `action:patchThumbnail` を追加。`safeRunCli` で argv 構築失敗を payload に丸めて renderer に返す
- `gui/args.cjs` — argv builder を Electron 非依存モジュールとして分離。smoke から直接 import 可能
- `gui/preload.cjs` — `setCompliance` / `registerMaterial` / `patchThumbnail` を contextBridge に追加
- `gui/renderer.{html,js}` — Rights / Materials / Thumbnail に action panel を追加。`prefillActionForms` が現在 episode から rights_manifest / episode_id / thumbnail_patch_input / output_result を自動 prefill
- 確認 dialog は単一の `#confirm-modal`。command 文字列 / summary / reason の 3 要素を表示。Esc=Cancel、Enter=Confirm。実行後は `action-result` 領域に exit / stdout tail / stderr tail を表示し、`status-episode` を自動 refresh
- `gui/styles.css` — action panel / form / modal スタイルを追加
- `gui/smoke.cjs` — Phase 2 マーカー（`data-action-form="..."` / `id="confirm-modal"`）の存在チェックと `args.cjs` の builder 検証を追加。Electron なしで完全 pass
- 危険操作 button（upload / fetch / bg-removal API）は依然不在（GUI_CONVENTIONS §5）
- 既存 Python 46 件 pass、JS syntax / smoke 全通過

### Slice 2 (a) Phase 1 done（ED-01 / ED-02a: edit_pack schema + manual cut input）

- `docs/SCHEMAS/v1/edit_pack.md` — cut 候補、選択 cut、字幕案、review 状態の schema を追加。
- `src/pipeline/edit_pack.py` — skeleton / load / save / validator / `add_cut_candidate`。時間範囲、cut/subtitle ID 一意性、選択 cut 参照、subtitle text、review approved 条件を検証。
- `src/cli/{init_edit_pack,validate_edit_pack,add_cut_candidate}.py` — `init-edit-pack` / `validate-edit-pack` / `add-cut-candidate` を追加。
- `src/pipeline/episode_status.py` / `src/cli/status_episode.py` — `edit_pack.json` の存在と schema 状態を status JSON / text に反映。
- `gui/renderer.js` — Episode dashboard に Editing status card を追加。ただし Editing tab はまだ出さない（操作可能に見せないため）。
- 累計テスト 46 件 pass。外部 API・元動画ダウンロード・speech-to-text・動画レンダリングは未実行。

### Slice 2 (c) Phase 1 done（SH-03: GUI MVP read-only console）

- `gui/` Electron skeleton — root `package.json`（Electron `42.0.0`）/ `gui/main.cjs`（IPC `episode:status`）/ `gui/preload.cjs`（contextBridge）/ `gui/{renderer.html,styles.css,renderer.js}`
- 5 タブ MVP — Episode（dashboard table）/ Rights / Materials / Thumbnail（readback table 含む）/ Settings（bridge readiness）
- `status-episode` JSON を spawn 経由で取得（cwd=リポ root）。Python は PATH または `CLIPPIPE_PYTHON` で指定
- `docs/GUI_CONVENTIONS.md` — 整合-A 規約（配色・状態語彙・タブ命名・readback 表示・危険操作・逆提案運用）
- Phase 2 = action 導線は **SH-03b** として proposed に分離。実行系 button は Phase 1 で意図的に出さない
- Python tests は 43 件 pass。GUI 側は `npm run smoke` / `npm run smoke:electron` で最小確認する。Playwright/jest 系は後続スライスで必要になってから判断。
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

### Slice 2 (c) done（SH-03: Electron GUI MVP skeleton）

- `package.json` — Electron 42.0.0 を dev dependency として定義。
- `gui/` — `main.cjs` / `preload.cjs` / `renderer.html` / `renderer.js` / `styles.css` / `smoke.cjs` を追加。
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

- SH-03b は GUI action 導線（init-edit-pack / add-cut-candidate / set-compliance / register-material / patch-thumbnail）だが、危険操作 button は置かない原則を維持する。
- ED-02 本体は speech-to-text / 自動検出 provider / NLE export を含む可能性があるため、着手前に provider と品質基準を決める。
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
