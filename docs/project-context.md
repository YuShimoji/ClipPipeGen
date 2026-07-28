---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-07-29
current_slice: ED-13
phase: evidence_linked_comparison_built_human_editorial_review_pending
active_branch: codex/s2-evidence-linked-comparison-v1
base_main_revision: 40fe3fbdf13631948d03641e33325e7f01ed9e56
implementation_revision: commit_containing_this_document
upstream_parity: no_upstream_local_only
health: EVIDENCE_LINKED_MULTI_SOURCE_COMPARISON_ARTIFACT_READY_FOR_HUMAN_REVIEW
---

# Project Context - ClipPipeGen

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、publishing準備をepisode単位で接続する制作補助ツールである。現在のED-13 / S2は、S1 persona-led digestを受理済みに変える作業ではない。S1で取得済みの二つの通常配信をexact provenanceへ戻せる比較IRへ結び、同じframe内で「第一印象」と「一週後の理解更新」を比較できるprivate review artifactを作る。

active identityは`clip-s2-subaru-evidence-linked-comparison-v1-002`。3 beatすべてで両sourceを同時表示し、一方のquoteだけをforeground audio ownerにする。primary quote、paired evidence、visible source/date label、exact time range、creator-authored propositionを別フィールドで保持する。S1 artifactはhuman review pendingのまま保存し、S2へacceptanceを継承しない。

## 到達済みの停止点

| 項目 | 状態 | 何が可能になったか |
|---|---|---|
| repository | start `40fe3fbdf13631948d03641e33325e7f01ed9e56`からlocal branch `codex/s2-evidence-linked-comparison-v1` | tracked CLI、renderer、tests、contractから再開可能。pushは未承認 |
| exact package | 63.466667s / MP4 SHA `a959dc50...72d00f` / 12 payload | 同一マシンでexact比較を全編review可能 |
| machine validation | manifest、full decode、focused regressions、wide/narrow browser、全transition/beat実frame inspectionがpass | 技術的reviewabilityを確認 |
| human decision | pending | 二画面比較、quote/support、audio ownership、三段の理解更新を判断する段階 |
| rights / production / public | closed | 技術greenから許諾・公開を推定しない |

## Campaign Horizon

1. ED-13 evidence-linked comparison explainer — comparison IRとexact evidence bindingを一例で検証する。
2. ED-14 synchronized multi-participant camera director — 同一eventの参加者cameraを時刻同期し、注目先を切り替える。
3. ED-15 event-centered reaction compiler — 一つのeventを中心に複数reactionを集約する。
4. ED-16 held-out genre variation proof — 別genreをheld outし、IRとreview contractの過適合を検出する。

comparison benchmark familyは「すばるかエレンか / みこちかスバルか / みこちかGACKTかローランドか」。multi-cameraは「ホロナルド / 7 Days to Die / Minecraft」。reactionは「ホロライブラジコン企画 / カードショップシミュレーター高額カード反応 / ドラゴンボール名場面反応」。すべて方向検証用のstaged scenarioで、source/rights availability、取得権限、production/public useを主張しない。

## 現在の最大gap

machine validationは「二sourceを同時frameへ正しくrenderし、各beatでaudio ownerを一つに限定した」ことを示す。まだ示していないのは「同時表示が理解を速め、primary quoteとpaired evidenceの関係が視聴者に自然に伝わり、三つのpropositionが一つの比較論になる」こと。この意味判断が現在のhuman gateであり、次のcode追加より先にexact MP4へverdictをbindする。

## 再開順

1. `AGENTS.md`
2. `README.md`
3. `docs/RUNTIME_STATE.md`
4. `docs/INVARIANTS.md`
5. `docs/AUTOMATION_BOUNDARY.md`
6. `docs/CURRENT_HANDOFF.md`
7. `docs/output_layer/S2_EVIDENCE_LINKED_COMPARISON.md`
8. `artifacts/ARTIFACTS.md`

同一マシンではS2 package、manifest、MP4 SHAをlive照合する。別端末ではGitに含まれない`episodes/`を利用可能と推定しない。

## 守る境界

- `episodes/`はignoredかつtracked 0件を維持する。
- S1 source/packageを上書き・削除せず、S1 human review pendingをS2から変更しない。
- NLMYTGenを含む他repositoryのfileを読まない・書かない。
- human verdictをsample frame観察やmachine validationで代替しない。
- rights、production subtitle/design/render、thumbnail、publishing、upload、public releaseをeditorial verdictから推定しない。
- Campaign benchmark名からsource availabilityや取得権限を推定しない。

## 次の依存順

`ED-13 exact human review -> bounded closure -> ED-14 camera synchronization contract -> ED-15 event/reaction contract -> ED-16 held-out variation proof`。各段階は別identity・別source/rights確認・別human gateを持つ。