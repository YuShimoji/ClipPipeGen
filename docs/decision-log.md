---
id: decision-log
title: Decision Log - ClipPipeGen
type: durable_decision_log
status: current
last_touched: 2026-07-15
---

# Decision Log - ClipPipeGen

## 2026-07-15 — OUT-08 の cut_009 source-time exception を廃止

supervisor correction により、`cut_009` が final decision `reject` のままであることと、
その素材を candidate へ使わないことを別契約として固定した。candidate 02 は
`81.298–98.315`、`98.315–116.467`、`116.934–135.219` の三範囲だけを使い、
旧 `137.054–138.055` / `sub_102` dependent payoff 例外は plan、validator、tests、
readback、HTML、current docs から除去した。

validator は authority ID、label、dependent flag より先に source-time overlap を
検査し、`cut_009` reject interval `135.219–144.000` と交差する range を render
前に拒否する。candidate 01 は再renderせず SHA-256 を保持し、candidate 02 の実装
baseline は remote commit `9ab8445afa247d07b46ef031cdc30f3fbbafafdd`。

状態は `OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY` で human
review pending、既存 acceptance boundary は不変。review package は tracked 0 の
same-machine evidence で、別ホストへ自動 transport されない。根拠:
`docs/RUNTIME_STATE.md` current capsule +
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md`

## 2026-07-15 — OUT-08 active / OUT-07 parked の regression 境界を固定

full suite で、OUT-07 時代の test が `artifacts/ACTIVE_REBUILD.json` を current
active contract として要求し続けていることが判明した。現行正本では OUT-08 の
same-machine package が active review evidence であり、同 JSON は OUT-07 の parked
predecessor contract である。test はこの二つを同時に検証する形へ更新する。

この変更は artifact、caption/cut authority、human decision、rights、production、
public/publishing gate を変更しない。根拠: `docs/RUNTIME_STATE.md` current capsule +
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md`

## 2026-07-14 — OUT-08 を review-ready で停止

OUT-08 は、既使用範囲を避けた real source authority から 2 本の vertical Shorts
internal review candidate を atomic package として生成する slice として完了した。
人間レビューに必要な映像・字幕・音声・境界・manifest readback は揃っているため、
次のボトルネックは実装ではなく candidate ごとの編集単位レビューである。

維持する状態:

- `human_review_pending=true`
- `authority_mutated=false`
- `cut009_final_cut_decision=reject`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_approval=pending`
- `public_or_publishing_acceptance=false`

この停止は、未観測の direct seek を自動で合格扱いせず、字幕の残存 review debt を
production typography の品質保証へ拡大しないためのものでもある。

## 2026-07-14 — OUT-07 を predecessor として固定

OUT-07 の main commit `4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9` は
`PARK_PROVISIONAL_USABLE`。この episode に対する canonical pattern、default
template、selected thumbnail とはみなさない。OUT-08 の active readback と
`artifacts/ACTIVE_REBUILD.json` の parked OUT-07 rebuild contract を混同しない。

## 2026-07-14 — remote 同期境界を確定

実装・docs・判断ログは branch
`codex/out-08-real-unused-range-short-minibatch-v0` の
`d3798c4cf1c622631b9a1089634909475d640b9f` にあり、upstream との距離は `0 0`。
`episodes/` は意図的に ignored のまま、tracked episodes は 0 件である。したがって
別端末で Git clone から再開できるのはコードと判断文脈までで、レビュー動画 package
は同一端末のローカル証拠として別途再生成または承認済み artifact transport が必要。

## 未解決の設計判断

人間が candidate 01 / 02 を一本の編集単位として評価し、必要ならテンポ・境界・字幕・
音声の違和感を自由記述する。その返答なしに candidate を selected、production、public、
publishing-ready へ遷移させない。
