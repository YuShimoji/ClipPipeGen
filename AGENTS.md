# AGENTS.md — ClipPipeGen

このファイルは AI エージェントの入口。境界・read order・再アンカリング手順を定める。運用ルールの正本は [docs/INVARIANTS.md](docs/INVARIANTS.md)、自動化境界は [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md)。

## スコープ境界

- **本リポは ClipPipeGen のみを扱う**。NLMYTGen を含む他リポのファイルは読まない・書かない。
- ユーザーが cross-project 作業を明示した場合のみ、その明示範囲だけ扱う。
- 再利用は **CLI subprocess 経由のみ**。NLMYTGen のソースコードを直接 import しない、コピーしない。

## 再開時の read order（最小）

1. [README.md](README.md) — 何のプロジェクトか
2. [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) — 現在のスライス・next_action
3. [docs/INVARIANTS.md](docs/INVARIANTS.md) — 非交渉条件
4. [docs/AUTOMATION_BOUNDARY.md](docs/AUTOMATION_BOUNDARY.md) — integration マップ・実装済／未実装の区分

これで足りない時のみ、必要な該当節だけ追加で読む：

- [docs/LANES.md](docs/LANES.md) — レーン責務の詳細
- [docs/FEATURE_REGISTRY.md](docs/FEATURE_REGISTRY.md) — 機能一覧
- [docs/FIRST_SLICE.md](docs/FIRST_SLICE.md) — 現スライスの実装計画
- [docs/SCHEMAS/v1/*.md](docs/SCHEMAS/v1/) — schema 詳細

## 事前確認が必要な操作

以下はリポジトリ破壊や範囲逸脱に直結するため、実行前にユーザー確認を取る：

- destructive git 操作（force push / reset / 履歴改変 / 未確認の大量削除）

## Git 運用

- 通常の commit / push は、スライス区切り・論理的にまとまった変更ごとに assistant 判断で実行してよい。
- main 直 push は許容する。ただし force push、履歴改変、他リポへの push は事前確認を取る。
- テストは過剰に増やさず、実装リスクに対して必要な最小 smoke / critical negative を優先する。

## やってはいけないこと

- NLMYTGen 側のファイル編集（CLI 呼び出しは可、編集は不可）
- cross-project 指示なしに他リポのファイルを読む・書く
- 実装済み CLI/GUI の挙動を docs だけで禁止扱いにする

## 命名規則（FEATURE ID）

| プレフィックス | レーン |
|---|---|
| CR-* | Compliance / Rights |
| MS-* | Material Sourcing |
| ED-* | Editing |
| TH-* | Thumbnail |
| PB-* | Publishing |
| INT-* | Integrations（外部 API・AI サービス境界） |
| SH-* | Shared infra（CLI runner・schema validator 等） |

NLMYTGen 側の FEATURE ID（A-* / B-* 等）とは独立。混同しない。

## 状態遷移

- `proposed` — 提案中。実装着手不可。
- `approved` — ユーザー承認済み。実装着手可。
- `in_progress` — 実装中。
- `done` — 実装＋acceptance 完了。
- `hold` — 一時停止。再開条件を明記する。
- `rejected` — 廃止。理由を残す。
- `successor-lane` — 別 ID として後継が起票された。本 ID は閉じる。

## 再アンカリング（context loss 時）

順序：

1. [README.md](README.md) を読む
2. [docs/RUNTIME_STATE.md](docs/RUNTIME_STATE.md) の `current_slice` と `next_action` を確認
3. 現スライスに直接関係する箇所だけ追加で読む
4. 不明点があればユーザーに確認、推測で書かない

## 報告コントラクト（workspace-wide、2026-05-11 設定）

実作業の報告（commit / push / hotfix / slice 進捗 / 機能追加）は単なる activity log では不足。以下を含める：

- **差分の焦点**：触った範囲と、意図的に触らなかった範囲
- **最終形 / North Star からの逆算した現在地**：この差分でプロジェクトの終着点にどこまで近づいたか。「step N の次」という時系列ではなく、ゴールから逆算した位置
- **検証 evidence**：readback、tests、smoke、push/sync 状態
- **残存リスク・未確定の判断**：stale な evidence、保留中の判断、ユーザー確認が要る箇所
- **次に推奨する hook**：assistant 視点で最も自然な次の一手
- **選択肢の分岐**：意味のある 2〜3 方向。直線的 next step を 1 つだけ示すのは不可
- **次の owner**：assistant / user / 両方

スライス区切り・handoff・明示的な closeout では追加で **機能状態の表**（実装済 / 進行中 / 未実装 / 棚上げ）を、現スライスまたは feature registry の該当節のスコープで出す。registry 全体ではなく slice scope にとどめる。

これは実作業の報告における既定の密度であり、機械的な template ではない。短い Q&A、lookup、方向性の探索質問はこれまで通り簡潔で良い。狙いはユーザーが追加プロンプト無しに次の move を判断できる前向きな文脈を渡すこと。Fixed audit form は引き続き anti-pattern だが、非自明な作業ではこの密度を default とする。

### Drift / overfitting self-check

スライス区切り・handoff・closeout では、以下の failure mode を自己診断し、該当するものは次の一手への影響と合わせて明示する（passive な脚注ではなく）：

- **case overfitting**: 個別題材／個別台本／個別 asset の審美調整に寄りすぎ、一般化していない
- **local optimization**: 工程内 artifact だけを磨いて North Star から外れている
- **docs-only loop**: 契約文書／spec／README だけが増え、実装 smoke・GUI ingest・YMM4 readback に戻れていない
- **standalone artifact completion**: 単発 HTML / PNG / JSON / fixture を、次工程への統合・proof path 無しで「完了」扱いしている
- **user-as-governor dependency**: ユーザーが毎回方向転換を検知しないと進めない状態になっている
- **next-artifact continuity**: 次工程の artifact・consumer・blocked reason が明確になっている

どれも発火していない場合はその旨を簡潔に書く。silent な self-check は self-check とみなさない。

### Recommended default path

意味のある分岐 2〜3 個を出すときは、assistant の **recommended default** を 1 つ明示し、理由を 1 行で添える（典型: North Star への最短経路 / blast radius 最小 / 下流の最多 unblock / standing preference 合致）。次の一手を以下に分ける：

- **assistant-owned**: standing approval の範囲内で assistant 単独で進められるもの
- **user-owned**: ユーザー判断・creative authorship・外部操作（GUI / YMM4 / 外部ツール）が要るもの

選択肢を等価な menu として並べてユーザーに丸投げするのは不可。

### Cross-project scope declaration

cross-project 作業では、報告冒頭に 1 行で scope を declare する（例: `Scope: NLMYTGen / WritingPage / ClipPipeGen`）。guardrails の cross-project pattern を満たす最小宣言にとどめ、毎回 cross-project の妥当性を再正当化しない。
