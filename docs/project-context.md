---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-21
current_slice: OUT-11
phase: human_review_ready
active_branch: codex/out-11-five-source-short-portfolio-wave-v0
verified_implementation_head: 249b3308b0d8a1cc8b75d37a245d717322859133
source_branch_tip: branch_tip_after_handoff_push
upstream_parity: 0 0
health: OUT11_HUMAN_REVIEW_REPAIRS_COMBINED_REVIEW_READY
contract_repair_status: source04_accepted_exact_bytes_out10_source05_repaired_two_candidate_review_built
---

# Project Context - ClipPipeGen

## 現在の軸・レーン・スライス

ClipPipeGenは、real source authorityからinternal review evidenceを作り、rights、production、
thumbnail、public/publishingの判断と混同せずに段階化する。現在の製品軸は複数sourceでの
Shorts候補再現性、担当レーンはoutput/video cross-source portfolio、現スライスはOUT-11である。
状態の正本は`docs/RUNTIME_STATE.md`、一手で再開する入口は`docs/CURRENT_HANDOFF.md`。

OUT-11初回レビューでは、SOURCE-04をexact bytes不変の`accepted_internal`受領証へ移し、
OUT-10とSOURCE-05の終端欠陥だけをbounded repairした。現在の唯一の判断面は、この修復二本を
同じlocalhostページで一度確認し、新しいexact SHAへ候補別の自由記述を結ぶことである。

| slot | source range | exact MP4 / 状態 | 次の判断 |
|---|---|---|---|
| OUT-10 | `youtube:TlnviOwLRmk` / `0.000–34.785s` | `62d4b45b...97cdd` / human review pending | 意識確認、患者反応、最終台詞が自然に閉じたか |
| SOURCE-04 | `youtube:PQ54uUV41-k` / `0.000–18.500s` | `465d732c...16524` / `accepted_internal`、bytes不変 | 再視聴・再renderしない |
| SOURCE-05 | `youtube:gUwJBRUIWow` / `202.586–260.643s` | `b4a01413...a4969` / human review pending | カード列からtitle/credit、source EOFまでが一単位か |

## 完了済みと保持する証拠

- 実装・tests・tracked docsの検証済みheadは
  `249b3308b0d8a1cc8b75d37a245d717322859133`。このhandoff更新は同headから作る。
- OUT-08/09は`accepted_internal` comparison contextとして閉じ、SOURCE-04も同状態。
- combined artifactは`clip-out11-five-source-short-portfolio-wave-v0-002`。readback SHAは
  `4e616091...b406`、scorecard SHAは`4b388531...d2c9`、manifest file/self SHAは
  `e72de3fe...a390` / `58276967...a7bd`。
- tracked code/docs/testsはremote branchから取得可能。`episodes/`はignoredでtracked 0件を維持する。

## 別端末との境界

別端末へGitで引き継がれるのは、builder、tests、正本docs、exact identity、受領証情報、再生成・
判断契約である。OUT-11のMP4、contact sheet、waveform、localhost packageは同一マシン限定で、
Git cloneには含まれない。したがって別端末ではコード・文脈から即再開できるが、同じ映像を
再生するには承認済みartifact transport方針または契約に沿った再生成が別途必要。

このinternal reviewからwinner、共通caption/crop/speaker-color policy、rights、production
render/subtitle/image quality、thumbnail、upload/OAuth/visibility/made-for-kids、public/publishing
を推論して開かない。SOURCE-05の歌唱・歌詞・speaker意味も未確認のまま保持する。

## 次の意思決定とその先

最短の次手は修復後OUT-10とSOURCE-05の一回レビューである。両方が受理された場合のみ、OUT-10
closureを先、OUT-11 closureを後にするmain統合計画を監修判断へ渡す。片方に違和感が残る場合は
そのcandidateだけをbounded repairまたはpark/rejectし、合格済み候補を再開しない。

その先は、5-source evidenceから一般化可能な字幕・構図規則とsource固有処理を分離し、
production subtitle/render、rights/material-use、thumbnail、private/unlisted deliveryを各々独立した
人間gateで一つずつ開く。最終像は、承認済みsourceからtraceableなepisode packとreviewable outputを
作り、rollback可能なreceiptを伴って公開判断へ渡すproduction-assist loopである。

## 別端末での最短再開

```powershell
git fetch --prune origin
git switch codex/out-11-five-source-short-portfolio-wave-v0
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

期待値はupstream parity `0 0`、tracked `episodes/` 0件。続けて`README.md`、
`docs/RUNTIME_STATE.md`、`docs/CURRENT_HANDOFF.md`を読み、人間判断が届いていなければ
acceptance状態を変更しない。
