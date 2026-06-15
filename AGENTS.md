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

## Worktree cleanup

- Cleanup rules are recorded in [docs/WORKTREE_CLEANUP_POLICY.md](docs/WORKTREE_CLEANUP_POLICY.md).
- Before code or docs edits, classify dirty state into active-scope tracked files, unrelated tracked modifications, untracked files, ignored generated/cache files, and active retained preview session artifacts.
- Restore unrelated tracked modifications and delete unrelated untracked/temp/cache files with path-scoped commands.
- Do not run broad ignored cleanup while an active `episodes/.../human_preview_session/` is retained for pending human review.
- Keep `episodes/` ignored and keep `git ls-files episodes` empty unless an explicit private/artifact-store strategy is approved.

## Agent operation / Prompt changes

- Agent operation rules are recorded in [docs/AGENT_OPERATION_CONTRACT.md](docs/AGENT_OPERATION_CONTRACT.md).
- Prompt and spec rewrite rules are recorded in [docs/PROMPT_CHANGE_MANAGEMENT.md](docs/PROMPT_CHANGE_MANAGEMENT.md).
- Reviewable artifacts are listed in [artifacts/ARTIFACTS.md](artifacts/ARTIFACTS.md).
- Do not stop at the first self-review, first test failure, or minor ambiguity when a reversible scoped fix is clear.
- True stop conditions are destructive operations, rights/publication judgment, credentials/OAuth/payment, cross-repo file access, production/public acceptance, active preview deletion, or repeated blockers after scoped fixes.
- Agent handoff prompts must contain only execution instructions. Monitoring comments, rationale, model UI wording, and supervision-only notes stay outside the prompt block.

## 完了報告フォーマット

非自明な作業では、以下の内容を自然な日本語見出しで実体ある内容として含める。空欄テンプレートとして並べない。

1. Summary
2. Changed files
3. Artifacts
   - artifact_id
   - repo_relative_path
   - preview_url or open_command
   - screenshot/contact-sheet/storyboard if applicable
4. Commands run and results
5. Validation
6. Decision packet, if user judgement is needed
7. Blockers, only if true stop condition
8. Next complete prompt for another Agent, only when handoff is requested

報告には internal reasoning settings、model UI terms、depth labels、unsupported claims、unverified full paths を含めない。

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

## 報告スタイル（workspace-wide、2026-05-11 設定）

報告はユーザーがファイルを開かなくても作業の意味が分かる自然文で書く。何を変えた / なぜ workflow・decision に効くか / 残る不確実性 / 次に進められる動き — これらを論理鎖として繋ぐ。

非自明な作業の報告では、以下を「実体ある内容」として出す (空ラベルの穴埋めではなく)：

- **比較表**: 変更・選択肢・残作業が複数あるときは、それらを表で並べる。列名は固定せず、実際の比較軸に合わせて選ぶ (例: `作業 / 目的 / 効果 / 必要条件 / 現在状態 / 次の動き`)。表は本文を補助するもので、本文の代替にしない。
- **次に推奨する作業 / 次の取っ掛かり**: 違う bottleneck を解く 2〜4 個の入口を提示する。例: `Advance` (進める) / `Audit` (見る) / `Excise` (削る) / `Explore` (広げる) / `Verify` (確かめる)。各入口について、どのワークフロー段階の摩擦が減るか・選ぶと次に何が可能になるかを短く添える。

禁止されているのは **機械的な空ラベルの穴埋め** — `summary` / `evidence` / `risk` / `next owner` / `assistant status` / `assistant next` / `差分の焦点` / `次の owner` のような固定英語ラベルや見出しを並べ、その下に薄い 1 行だけ書く形式。これらは内部チェック項目であり出力フィールドではない。日本語の自然な節タイトルを使い、各節の中身を実体で埋める。`P0/P1`・bare path list・test 名だけを説明にしない (証跡として後置するのは可)。

短い Q&A、lookup、方向性の探索質問はこの限りではなく、これまで通り簡潔で良い。

cross-project 作業の冒頭 1 行 scope 宣言 (例: `Scope: NLMYTGen / WritingPage / ClipPipeGen`) は、guardrails の cross-project pattern を満たす最小宣言として使う。毎回再正当化しない。

スライス区切りでは drift を内部チェックする (個別ケース過剰調整 / 工程内最適化 / docs だけ増えて実装に戻れていない / 単発 artifact を統合無しで完了扱い / ユーザーが毎回方向検知を強いられる / 次工程の consumer 不明確)。発火している項目だけ次の一手への影響と合わせて自然文で触れる。発火がなければその旨を一文で済ます。固定見出しを並べる出力はしない。
