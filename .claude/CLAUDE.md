# CLAUDE.md（Claude Code 用入口）

**運用ルール正本**: [docs/INVARIANTS.md](../docs/INVARIANTS.md) / [docs/AUTOMATION_BOUNDARY.md](../docs/AUTOMATION_BOUNDARY.md)
**プロジェクト方針**: [CLAUDE.md](../CLAUDE.md)（ルート）
**エージェント入口**: [AGENTS.md](../AGENTS.md)

本ファイルはツールが慣例で読む薄い入口。詳細は上記を参照。

## 最小ルール

- 本リポ以外（特に NLMYTGen）のファイルは読まない・書かない。NLMYTGen 再利用は CLI subprocess 経由のみ。
- 通常再開は **README.md → docs/RUNTIME_STATE.md** で止める。INVARIANTS / LANES / FIRST_SLICE は必要時のみ。
- `proposed` 機能は実装着手しない。承認後に `approved` へ昇格してから着手する。
- 危険な操作（外部 API 呼び出し・upload・push・元動画ダウンロード）は必ずユーザー確認を取る。
- `compliance_check.status != passed` の manifest／素材を upload／publish 系 CLI に渡さない。
- `.ymmp` ゼロ生成禁止。
