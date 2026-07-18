---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-19
current_slice: OUT-09
active_branch: main
source_branch_tip: 17436ad482f5e10db12b1461ec3caee18ae932d3
upstream_parity: 0 0
health: OUT09_ACCEPTED_INTERNAL_CANONICAL_MAIN
contract_repair_status: OUT09_REVIEW_ACCESS_STABILITY_AND_PLAYBACK_SAFETY_REPAIR_PASSED
---

# Project Context - ClipPipeGen

## 現在地

ClipPipeGenは、real source authorityからinternal review evidenceを作り、rights、
production、public/publishingの判断と混同せずに段階化する。現在の正本は
`docs/RUNTIME_STATE.md`、再開点は`docs/CURRENT_HANDOFF.md`である。

OUT-09ではOUT-08と異なるreal sourceから一本のvertical Shortを生成し、caption presentationと
manual-safe review accessを修復したexact MP4についてユーザーacceptanceを受領した。字幕音声一致、
短cue切替・可読性、初期無音、foreground access、終端はいずれも期待どおりで、
`accepted_internal`としてmainへ着地する。

| candidate | source | media duration | subtitles | SHA-256 |
|---|---|---:|---:|---|
| OUT-09 `candidate_01` | `D4i4fjs9PWc` | `33.333008s` | 27 | `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50` |

## 境界

ignored packageやserverの停止は受入を失効させない。rightsは`pending`。production render、
production subtitle design/image quality、thumbnail、public/publishing、upload/OAuth/visibility/
made-for-kidsは閉じたまま。

上下のblur/mosaic canvasはsource下部74pxのcaption bandを除外したsource-specific処理として
今回だけacceptableで、全動画共通designではない。caption bandのないsource、cropと重要内容が
衝突するsource、production subtitle designへ自動適用しない。OUT-07は
`PARK_PROVISIONAL_USABLE` predecessorのままである。

## 次の製品軸

data-only successorは`OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION`一件だけ。第三のdistinct
real sourceから最低1本の12〜60秒・9:16 candidateを作り、caption authority、crop strategy、
cue density、source resolution、render time、人間結果をOUT-08/09と共通schema比較する。
現時点では未実装で、実装承認ではない。

その先の完成像は、単一episodeで成功したbuilderを複数sourceへ一般化し、3〜5本の
real Shorts portfolioで字幕・境界・thumbnailの再現性を比較した後、production render、
rights/material-use、thumbnail、private/unlisted publishingをそれぞれ独立した人間gateで
開くこと。最終的には、承認済みsourceからtraceableなepisode packとreviewable outputを
作り、rollback可能なreceiptを伴って公開判断へ渡せるproduction-assist loopを目指す。

2026-07-19のmerge-preflightでは、origin/main `29a1a519`とOUT-09 branch `17436ad`で既知
OUT-06 2 testsが同一失敗し、default vertical render command SHAが一致した。branch-only
regressionはなく、OUT-06 debtはparkする。現状・不足・段階目標の詳細は
[SUPERVISOR_STATUS_REPORT.md](SUPERVISOR_STATUS_REPORT.md)に集約する。

再開時は`git switch main`、`git pull --ff-only origin main`の後、RuntimeとCurrent
Handoffを読む。NLMYTGenのsourceを直接import・copyせず、必要な再利用はCLI subprocess
境界だけに保つ。
