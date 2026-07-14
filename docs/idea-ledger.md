---
id: idea-ledger
title: Idea Ledger - ClipPipeGen
type: durable_idea_ledger
status: current
last_touched: 2026-07-15
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

## Long-horizon goal ladder（未承認提案）

これは先の開発順序を監修するための目標階層であり、FEATURE の `approved` や
production/public 操作の許可ではない。前段の evidence と human decision が揃った
時だけ次段を起票する。

| 地平 | 目的と得られる効果 | 必要条件 | 現在状態 / owner | 次の動き |
|---|---|---|---|---|
| H0: OUT-08 decision closure | candidate 01 / 02 を accept-internal、bounded repair、park/reject のいずれかへ分け、単発の感想を実装可能な decision にする | 人間が二本を direct playback し、candidate ごとに自由記述する | human review pending / owner: user | 返答を受けた Agent がテンポ・境界・字幕・音声の debt を分離し、一度の bounded successor slice か closure を提案 |
| H1: real Shorts portfolio 3–5 本 | 一作品・一候補への過適合を避け、編集テンポ、字幕、cover の再利用可能性を比較できる母数を作る | H0 closure、少なくとも 3 本、できれば複数 source episode、rights readback 維持 | 2 本 review-ready + OUT-06 predecessor / owner: Editing + output integration | accepted/parked/rejected の理由、尺、境界、字幕密度、視覚方向を共通 scorecard に集約。3–5 本到達後だけ OUT-07 thumbnail exploration 再開を審査 |
| H2: production limitation lift | diagnostic/internal success を production subtitle design、production render、rights clearance の独立 acceptance に変える | H1 の再現 evidence、font/license 方針、safe-area/line-break policy、A/V/seek/full-decode 基準、episode rights review | gates closed / owner: user + Compliance + Editing/output integration | subtitle design → render → rights の順に別 decision packet を作り、どれか一つの pass を他 gate へ波及させない |
| H3: portable episode delivery | Git 外の source-derived package を provenance、access、retention、rollback 付きで別端末へ渡し、同じ episode を再開可能にする | private artifact store / transport の明示承認、`episodes/` public Git 禁止の維持、episode_pack contract | transport hold、`SH-02` proposed / owner: Shared infra + user | private storage 方針が承認された場合だけ、tracked manifest と private payload receipt を分けた portable handoff を起票 |
| H4: controlled private publishing rehearsal | production-accepted video、thumbnail、metadata を private/unlisted upload と receipt まで接続し、公開前 rollback を実証する | H2/H3 完了、PB-01 metadata draft、INT-01 OAuth、credentials、rights/publication の明示承認 | PB-01..04 / INT-01 proposed / owner: user + Publishing integration | metadata-only dry-run を先に行い、その後に private/unlisted upload、thumbnail set、visibility/readback、rollback receipt を別 gate で実行 |
| H5: multi-episode production loop | source intake から review、production acceptance、private publish receipt までを複数 episode で反復し、制作時間と人間判断点を減らす | H4 成功、official caption が無い素材向け STT quality route、failure/recovery telemetry | north-star proposal / owner: all lanes | episode ごとに source→ledger→transcript→edit→review→production→publish の lead time、手動判断数、再生成一致率、recovery 成功率を測り、2–3 episode で繰り返した境界だけ共通化 |

到達点は「ボタン一つの公開」ではなく、各 gate の owner と証跡を失わず、別端末でも
復旧でき、複数 episode で同じ手順を繰り返せる production-assist loop である。

## 意図的に増やさないもの

production render、production subtitle design、rights/public/publishing、upload、
thumbnail acceptance、GUI one-click action は、OUT-08 の review response から自動的に
派生させない。docs の増量だけで進捗扱いにせず、次の実装は必ず operator decision を
`edit_pack`、subtitle draft、render plan、NLE handoff のいずれかへ戻す。
