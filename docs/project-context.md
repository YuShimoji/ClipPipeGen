---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-17
current_slice: OUT-08
active_branch: main
source_branch_tip: 2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2
upstream_parity: 0 0
health: OUT08_ACCEPTED_INTERNAL_CANONICAL_MAIN
contract_repair_status: OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY
---

# Project Context - ClipPipeGen

## 現在地

ClipPipeGenは、real source authorityからinternal review evidenceを作り、rights、
production、public/publishingの判断と混同せずに段階化する。現在の正本は
`docs/RUNTIME_STATE.md`、再開点は`docs/CURRENT_HANDOFF.md`である。

OUT-08では未使用実素材から二本のvertical Shortsを生成し、`cut_009` reject intervalを
完全除外した修復後exact bytesについて、ユーザー回答「両方問題ありません」を受領した。
batchは`accepted_all_internal`、candidate 01 / 02はともに`accepted_internal`、winnerは
none。OUT-08はaccepted-internal closureとしてmainへ着地する。

| candidate | media duration | subtitles | SHA-256 |
|---|---:|---:|---|
| `candidate_01` | `28.266667s` | 17 | `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` |
| `candidate_02` | `53.466667s` | 54 | `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` |

## 境界

Planner007でpackageが欠けていることは再視聴不能を示すだけで、受入を失効させない。
recovery branch `d1f44d1`は任意・非canonical infra proofとしてparkし、mainへ統合しない。
rightsは`pending`。production render、production subtitle design、thumbnail、public/
publishing、upload/OAuth/visibility/made-for-kidsは閉じたまま。

`sub_067` / `sub_068`はこのexact render内で受入済みだが、全動画共通ルールではない。
OUT-07は`PARK_PROVISIONAL_USABLE` predecessorのままで、3〜5本のreal Shortsが揃うまで
thumbnail explorationを再開しない。

## 次の製品軸

data-only successorは`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY`。異なるsourceまたは
episodeから、既存Shorts pipelineを大規模に書き換えず、最低1本の12〜60秒・9:16・
reviewable candidateを生成できることを将来のacceptance signalとする。現時点では
proposalであり、実装承認ではない。

再開時は`git switch main`、`git pull --ff-only origin main`の後、RuntimeとCurrent
Handoffを読む。NLMYTGenのsourceを直接import・copyせず、必要な再利用はCLI subprocess
境界だけに保つ。
