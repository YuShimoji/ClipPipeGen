# Runtime State — ClipPipeGen

ブロックの主成果と次の手を更新する。compact 後の再アンカリングではこのファイルを読む。

## 現在位置

### Bootstrap（リポ初期化）

- リポ作成済み（GitHub 上）
- 初期方針書一式を配置（README / CLAUDE.md / AGENTS.md / .claude/CLAUDE.md / docs/INVARIANTS / LANES / AUTOMATION_BOUNDARY / FEATURE_REGISTRY / SCHEMAS/v1 / FIRST_SLICE）
- まだコミット・プッシュしていない（ユーザー review 待ち）
- 実装コードはまだ書いていない

### project

- name: ClipPipeGen
- repo: https://github.com/YuShimoji/ClipPipeGen
- 並列ローカルパス: `c:\Users\thank\Storage\Media Contents Projects\ClipPipeGen`
- 関連リポ: [NLMYTGen](https://github.com/YuShimoji/NLMYTGen)（CLI subprocess 経由でのみ再利用）

### lane / slice

- **current_lane**: Bootstrap
- **current_slice**: Slice 1 — Material Sourcing + Thumbnail 最小実証（[FIRST_SLICE.md](FIRST_SLICE.md)）
- **next_action**: ユーザーが初期ドラフトを review し、(a) リポへのコミット可否、(b) FEATURE_REGISTRY 内の Slice 1 関連項目（CR-01 / MS-01..03 / TH-01）の `proposed → approved` 昇格を判断する。承認後、Slice 1.1（rights_manifest schema 適用）から実装着手。

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
