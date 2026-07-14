---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-14
current_slice: OUT-08
active_branch: codex/out-08-real-unused-range-short-minibatch-v0
head: d3798c4cf1c622631b9a1089634909475d640b9f
upstream_parity: 0 0
health: OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY
---

# Project Context - ClipPipeGen

この文書は、別端末・別セッションで最初に読むための短いプロジェクト文脈である。
現在の状態値と詳細な証跡は `docs/RUNTIME_STATE.md`、現在の停止点は
`docs/CURRENT_HANDOFF.md`、OUT-08 のレビュー契約は
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md` を正本とする。

## 軸・レーン・スライス

- 軸: real source authority からの internal review evidence を、rights / production /
  publishing の判断と混同せずに積み上げる。
- レーン: Shared infra / output layer。ClipPipeGen のみを扱い、NLMYTGen は CLI
  subprocess 境界の外へ持ち込まない。
- 現在のスライス: `OUT-08 real unused-range vertical Shorts mini-batch`。
- 状態: target 2 / minimum 1 に対して candidate 01 と 02 の 2 本を生成済み、
  人間レビュー待ち。`production_candidate=false`、rights は `pending`。

## いま成立していること

artifact `clip-out08-real-unused-range-short-minibatch-v0-001` は、ignored な同一端末
レビュー package に保存されている。candidate 01 は `cut_004 -> cut_005` の
28.266667 秒、candidate 02 は `cut_006` tail、`cut_007`、`cut_008` と
`sub_102` の dependent payoff からなる 54.5 秒である。`cut_009` は reject のまま
で、authority は変更していない。両候補は H.264/AAC 1080x1920 30fps、full decode、
black/silence bounded check、HTTP 200 / Range 206 を通過している。

字幕の明確な語中分断には bounded repair を適用したが、`sub_067` の「特殊 / な」
と `sub_068` の「ホロ / モワール」は review debt として残す。これは production
typography acceptance ではない。browser の readyState / overflow / console 証跡は
repair 前の確認を含み、最終 package の direct seek は自動観測できていないため、
開始・境界・終端の自然さは人間レビューに残る。

## 再開契約

新しい端末では、まず次を実行する。

```powershell
git fetch --prune origin
git switch codex/out-08-real-unused-range-short-minibatch-v0
git pull --ff-only
git status --short --branch
git rev-list --left-right --count "HEAD...@{u}"
git ls-files episodes
```

その後、`README.md` → `docs/RUNTIME_STATE.md` → `docs/INVARIANTS.md` →
`docs/AUTOMATION_BOUNDARY.md` → `docs/CURRENT_HANDOFF.md` の順で読む。ローカル
package が存在する端末では、次でレビューを再開する。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out08_real_unused_range_short_minibatch\open_preview.ps1 -Port 8071
```

`episodes/` は Git 管理外なので、別ホストには動画・字幕・manifest は自動では移ら
ない。別ホストでそれらが無いことは remote code failure ではなく、同一端末ローカル
証拠の不在である。再生成する場合だけ、OUT-08 の build contract と source hash を
再確認し、別 artifact として扱う。

## 人間判断と閉じた境界

次の入力は candidate ごとの自由記述だけでよい。一本の編集単位として成立するか、
テンポ・境界・字幕・音声の違和感を記録する。人間判断が返るまで、rights、production
render、production subtitle design、public/publishing、upload、thumbnail acceptance
は開かない。OUT-07 は `PARK_PROVISIONAL_USABLE` の parked predecessor であり、
real Shorts が 3–5 本に達するまで追加 thumbnail iteration を再開しない。
