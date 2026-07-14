---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-14
---

# Idea Ledger - ClipPipeGen

ここでは、次に進められる高シグナルの入口だけを保持する。提案は承認済み実装と
同義ではない。

| 入口 | 目的 / 効果 | 必要条件 | 現在状態 | 次の動き |
|---|---|---|---|---|
| Advance: OUT-08 candidate review | 2 本を編集単位として判断し、次の修正対象を一つに絞る | 人間が review page を再生し、candidate ごとに自由記述する | 最優先、human review pending | `http://127.0.0.1:8071/index.html` を開き、テンポ・境界・字幕・音声を記録 |
| Verify: 同一端末 package readback | 取り込み後のローカル証拠が docs の hash / manifest と一致することを確認する | ignored package が存在する端末、または OUT-08 build inputs | 実装済み、direct seek の自動証跡だけ未観測 | `batch_manifest.json`、HTTP Range、ffprobe を再確認。再生成時は新 artifact として記録 |
| Audit: review response normalizer | 自由記述を candidate 単位の decision packet に変換し、修正範囲を明示する | 人間レビューの具体的な返答 | 未着手、OUT-08 判断後 | review debt / boundary / subtitle / audio の各修正を別 decision として正規化 |
| Explore: cross-machine evidence transport | ignored video package を別ホストでも再現可能にする | private artifact store 等の明示承認、provenance と access policy | 保留。現状は portable_local_artifact_available=false | ユーザーが transport 方針を承認した場合だけ、artifact handoff 契約を追加 |
| Defer: OUT-07 thumbnail iteration | 早期の一枚の成功を canonical rule にしない | real Shorts が 3–5 本、別途 thumbnail 判断 | 明示的に parked | OUT-08 / 後続 real Shorts を先に増やす |

## 意図的に増やさないもの

production render、production subtitle design、rights/public/publishing、upload、
thumbnail acceptance、GUI one-click action は、OUT-08 の review response から自動的に
派生させない。docs の増量だけで進捗扱いにせず、次の実装は必ず operator decision を
`edit_pack`、subtitle draft、render plan、NLE handoff のいずれかへ戻す。
