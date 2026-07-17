---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-17
current_slice: OUT-08
active_branch: codex/out-08-private-review-package-recovery-v0
verified_remote_head: 180bd28228642a4689246ceaf31babc47a044531
upstream_parity: 0 0
health: OUT08_PRIVATE_REVIEW_PACKAGE_RECOVERY_READY
contract_repair_status: OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY
---

# Project Context - ClipPipeGen

この文書は、別端末・別セッションで最初に読むための短いプロジェクト文脈である。
現在の状態値と詳細な証跡は `docs/RUNTIME_STATE.md`、現在の停止点は
`docs/CURRENT_HANDOFF.md`、OUT-08 の復旧契約は
`docs/output_layer/OUT_08_PRIVATE_REVIEW_PACKAGE_RECOVERY.md` と
`docs/output_layer/out08_private_review_package_recovery_contract.json` を正本とする。

## 軸・レーン・スライス

- 軸: real source authority からの internal review evidence を、rights / production /
  publishing の判断と混同せずに積み上げる。
- レーン: Shared infra / output layer。ClipPipeGen のみを扱い、NLMYTGen は CLI
  subprocess 境界の外へ持ち込まない。
- 現在のスライス: `OUT-08 exact private review package recovery`。
- 状態: Thank で target 2 / minimum 1 に対して candidate 01 と 02 の 2 本を exact
  package として検証済み。Planner007 では package が無く、私的移送と atomic import
  の後に人間レビューする。`production_candidate=false`、rights は `pending`。

## いま成立していること

source artifact `clip-out08-real-unused-range-short-minibatch-v0-001` は、Thank の ignored
同一端末レビュー package に保存されている。candidate 01 は `cut_004 -> cut_005` の
28.266667 秒、candidate 02 は `cut_006` tail、`cut_007`、`cut_008` だけからなる
53.466667 秒である。`cut_009` は reject のまま、全 source range は reject interval
`135.219–144.000` と非交差で、authority は変更していない。両候補は H.264/AAC
1080x1920 30fps、full decode、
black/silence bounded check、HTTP 200 / Range 206 を通過している。

字幕の明確な語中分断には bounded repair を適用したが、`sub_067` の「特殊 / な」
と `sub_068` の「ホロ / モワール」は review debt として残す。これは production
typography acceptance ではない。browser の readyState / overflow / console 証跡は
repair 前の確認を含み、最終 package の direct seek は自動観測できていないため、
開始・境界・終端の自然さは人間レビューに残る。

2026-07-15 の contract repair では、source-time overlap validator を authority ID、
label、dependent flag より先に適用し、candidate 01 を再renderせず SHA-256
`f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a`
のまま保持した。candidate 02 は semantic `53.454s`、54 subtitles、SHA-256
`47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b`。
targeted tests 8、changed-scope Ruff、manifest、ffprobe/full decode、browser
desktop/mobile check が pass した。server は Thank の exact route / port `8071` で
page HTTP `200` と MP4 Range `206` を確認済みで、listener PID は可変値として
正本化しない。

後継 artifact `clip-out08-private-review-package-recovery-v0-001` は、17-file / 16-payload
package、manifest self-integrity、candidate hashes、Thank host、`cut_009` source-time
完全除外を export と import staging の両方で検証する。export は explicit な repo 外
ZIP、import は unsafe archive を拒否して fully verified sibling stage だけを atomic
promotion する。Planner007 の current probe は `package_missing` / `server_stopped` で、
current localhost entrypoint は存在しない。これは remote code failure ではなく
`recovery_kit_ready_package_not_yet_imported` である。現行 remote HEAD は `180bd28`。

## 再開契約

新しい端末では、まず次を実行する。

```powershell
git fetch --prune origin
git switch codex/out-08-private-review-package-recovery-v0
git pull --ff-only
git status --short --branch
git rev-list --left-right --count "HEAD...@{u}"
git ls-files episodes
uvx python -m src.cli.main recover-out08-private-review-package --format json probe
```

その後、`README.md` → `docs/RUNTIME_STATE.md` → `docs/INVARIANTS.md` →
`docs/AUTOMATION_BOUNDARY.md` → `docs/CURRENT_HANDOFF.md` の順で読む。Planner007 で
package が無い場合は Thank で repo 外 ZIP へ export し、利用者が選ぶ private channel
で一度コピーしてから atomic import を行う。

```powershell
# Thank
uvx python -m src.cli.main recover-out08-private-review-package --format json export --destination D:\private-transfer\out08-review.zip

# Planner007 after private copy
uvx python -m src.cli.main recover-out08-private-review-package --format json import --archive D:\private-transfer\out08-review.zip --start-server
```

`episodes/` は Git 管理外なので、別ホストには動画・字幕・manifest は自動では移ら
ない。別ホストでそれらが無いことは remote code failure ではなく、同一端末ローカル
証拠の不在である。private transport の選択、upload、credentials は利用者の領域で、
payload を Git へ追加しない。import 後の probe が `package_verified_exact` /
`server_running_verified` になった場合だけ preview を開く。別 source から再生成した
候補を exact package と主張しない。

## 人間判断と閉じた境界

次の入力は candidate ごとの自由記述だけでよい。一本の編集単位として成立するか、
テンポ・境界・字幕・音声の違和感を記録する。人間判断が返るまで、rights、production
render、production subtitle design、public/publishing、upload、thumbnail acceptance
は開かない。OUT-07 は `PARK_PROVISIONAL_USABLE` の parked predecessor であり、
real Shorts が 3–5 本に達するまで追加 thumbnail iteration を再開しない。
