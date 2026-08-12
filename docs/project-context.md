---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-08-12
current_slice: ED-13
phase: wiki_cu04_proof_portable_handoff_semantic_route_unresolved
active_branch: codex/wiki-tensaku-longform-family-v1
sync_observed_head: c307089a592bb73b6539f801ff32b461dc4a424d
upstream_parity: 0 0
health: WIKI_CU04_PROOF_REVIEW_USEFUL_SEMANTIC_ROUTE_UNRESOLVED_EP1_SOURCE_GATE_PARKED
---

# Project Context - ClipPipeGen

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。現在のWiki添削familyは、
全配信規模を理解可能なEpisodeへ再構成するED-13にいる。

Episode 1「Wikiが作る人物像」のcanonical integrated cutは、CU-02
`youtube:Ocqg-RpQURY` 390–585秒のexact mediaと隣接receiptがないためfail-closedでpark中。
その代替として別素材を採用していない。一方、retained exact source
`youtube:1AcId5Yja10`から、cut・字幕・testを同じcandidate identityで比較できる
`clip-wiki-integrated-subtitle-cut-proof-v1-001`を作成済みである。

## 最新のmaterial result

| 項目 | exact state | 意味 |
|---|---|---|
| proof package | `episodes/integrated_checklist_reverse_test_20260811/artifacts/cpg-integrated-checklist-reverse-test-v1/successors/cpg-integrated-subtitle-cut-proof-continuation-v1/package/` | Git外のreview material |
| current manifest | 69 payload members + manifest / SHA `534882f9be1e36ed773a7b59b418ea1e6e203d64b7f4f690def0674c67bace52` | loopback launcher/serverを含むclosed set |
| review surface | `review/index.html` / SHA `a5d0db6bca005b95aeae51155b52325d64a30e9be1d16608a096411a4b26d26f` | timestamp-jumpable comparison |
| four MP4s | `b2dbc8aa...48aedb`, `cc31dedc...af882`, `1c3f6a00...eb10a1`, `2cafe893...70f52` | opening、causal core、二つのendpointを実字幕で比較 |
| Reviewer result | `PROOF_SET_REVIEW_USEFUL_SEMANTIC_ROUTE_UNRESOLVED` | proofは有用、semantic winnerは未決 |

dispatch時のpre-access manifest `3d98c204...9a544`は、MP4やreview HTMLを変えず
loopback launcher/serverを追加したaccess-only successorに置き換わった。live closed identityは
上表の`534882f9...ace52`であり、古いmanifestへ巻き戻さない。

## 現在のgapと境界

- openingの2523.480開始と2530.319開始のどちらが理解を助けるかは人間判断。
- event_001639完結とevent_001641侵入回避のどちらを採るかも人間判断。
- 字幕timing、改行、幅、burn-in、full decodeはtechnical evidenceであり、semantic winnerや
  human artistic acceptanceではない。
- 親338.166016秒のfull-1x review queueは別gateで、短尺proofでは代替・再pollしない。
- rights、production subtitle/design/render、delivery、publication、monetization、uploadは未承認。
- Episode 1のCU-02 exact-source gateは、このindependent proofによって解消した扱いにしない。

## 別端末での最短再開

1. `README.md` → `docs/RUNTIME_STATE.md` → `docs/CURRENT_HANDOFF.md`を読む。
2. Gitのbranch / HEAD / upstream parityと`git ls-files episodes`が0件であることを確認する。
3. 親CoordinatorからClipPipeGen portable ZIPと外部manifestを受け取り、manifest記載のSHA、
   member count、relative pathsを検証する。Git cloneだけではreview mediaは得られない。
4. ZIP内`package/review/open_review.ps1`を使いloopback HTTPでreviewを開く。
5. openingとendpoint policyへのhuman semantic verdictをexact MP4 SHAへbindする。

## 次の依存順

`portable packet readback -> human semantic route decision -> selected routeだけをnew identityで
materialize -> separate full-1x/content review`がproof laneの最短経路である。
Episode 1本線は独立して`Ocqg-RpQURY exact bytes + receipt -> preflight rerun -> integrated render`。
どちらからもrights、production、publicationを推定しない。
