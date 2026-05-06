# Runtime State — ClipPipeGen

ブロックの主成果と次の手を更新する。compact 後の再アンカリングではこのファイルを読む。

## 現在位置

### Slice 1.1 done（CR-01: rights_manifest schema＋validator＋CLI）

- Bootstrap commit 済（`d5efd86`、main）
- Slice 1 features 全て `approved` 昇格済（CR-01 / MS-01 / MS-02 / MS-03 / TH-01 / SH-01）
- 軽量 review 通過：CLI 命名統一（`audit-ledger` → `audit-material-ledger`）、schema 名・レーン境界・Gate 強制方式は変更なし
- **CR-01 実装完了**：
  - `src/pipeline/rights_manifest.py` — schema validator / auto-fail evaluator / `set_compliance_status` / `assert_compliance_passed` (gate)
  - `src/cli/{main,init_episode,validate_rights,set_compliance}.py`
  - `tests/test_rights_manifest.py` — 9 tests, all passing
- gate enforcement 確認済：`status != passed` → `ComplianceGateError`、`vod_status in {private, members_only, deleted}` または `third_party_ip[].permitted == false` で `set-compliance --status passed` が拒否される

### project

- name: ClipPipeGen
- repo: https://github.com/YuShimoji/ClipPipeGen
- 並列ローカルパス: `c:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`
- 関連リポ: [NLMYTGen](https://github.com/YuShimoji/NLMYTGen)（CLI subprocess 経由でのみ再利用）

### lane / slice

- **current_lane**: Material Sourcing
- **current_slice**: Slice 1 — Material Sourcing + Thumbnail 最小実証（[FIRST_SLICE.md](FIRST_SLICE.md)）
- **current_sub_slice**: Slice 1.2 — MS-01 / MS-02 / MS-03（material_ledger + sidecar + 透過PNG 受け入れ）
- **next_action**: Slice 1.2 着手。`material_ledger.py` + `material_sidecar.py` + `register-material` / `audit-material-ledger` CLI を実装し、CR-01 と同じ最小テスト方針（positive 1 + critical negatives）で検証する。完了後 Slice 1.3 = TH-01（NLMYTGen bridge）。

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
