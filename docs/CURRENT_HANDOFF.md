---
id: current-handoff
title: Current Handoff - ClipPipeGen
type: handoff
status: active
health: OUT14_PUSH_MICROARC_EDITORIAL_V2_READY_FOR_HUMAN_REVIEW
last_touched: 2026-07-27
current_slice: OUT-14
phase: exact_v2_artifact_human_editorial_review_pending
active_branch: codex/out14-push-microarc-editorial-v2
exact_branch_base: 30b4891399ad474b624518f7dcb76591b68c8bef
active_artifact: clip-out14-push-microarc-editorial-v2-001
acceptance_media_sha256: 8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414
human_review_pending: true
editorial_acceptance_granted: false
rights_approval: false
production_acceptance: false
public_or_publishing_acceptance: false
remote_mutation_authorized: false
source_of_truth: true
owner_lane: human_editorial_language_title_thumbnail_review
next_action: review_exact_v2_artifact_and_bind_one_verdict_to_exact_sha
---

# Current Handoff - ClipPipeGen

## 監修役が最初に確認するもの

レビュー対象は
`episodes/out14_push_microarc_editorial_v2_20260727/artifacts/clip-out14-push-microarc-editorial-v2-001/review/index.html`。
起動は次のどちらか。

```powershell
powershell -NoProfile -File episodes\out14_push_microarc_editorial_v2_20260727\artifacts\clip-out14-push-microarc-editorial-v2-001\review\open_preview.ps1
```

```powershell
uv run python -m src.cli.serve_review `
  --root episodes/out14_push_microarc_editorial_v2_20260727/artifacts/clip-out14-push-microarc-editorial-v2-001 `
  --port 8081
```

server実行中のURLは`http://127.0.0.1:8081/review/index.html`。
確認済みのfinal MP4 SHAは
`8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414`、
manifest SHAは
`774351a7fc55839e05e58276280570a27ac1fd0aa7fa78283cdcf79f5d8634a9`。

## なぜ v2 になったか

v1はsource取得、reverse mapping、render/decode、A/V、localhost deliveryには成功したが、
人間のeditorial reviewで「連続11分の字幕付き抜粋」「episode境界が見えない」
「字幕が発話より遅い」「猿と喧嘩・アライグマ等の誤認」「非発話annotation表示」と判定された。
技術greenを消さず、editorial rejectionを
`docs/output_layer/OUT_14_V1_HUMAN_EDITORIAL_DECISION.json`へappend-onlyで固定した。
v1はarchive reachableだがcanonical/default/release candidateではない。

v2は3 stream identityから9 episode candidateを作り、hard gate後の100点rubricで比較した。
selected C3は93点。v1 span overlap 0で、Discordプロフィールをおかゆと変更し、
通知がスタッフや外部フレンドへ届いたと知って謝罪・注意へ閉じる因果を選んだ。
11件の競合観測をselection recordと分離保存した。

## exact artifact の中身

| 観点 | 確定値 | 監修への意味 |
|---|---|---|
| source | anonymous `399+251`、1920x1080/60、AV1/Opus、642.001秒窓 | native HD。cookies/OAuth/credentialなし |
| 時刻原点 | protected v1音声との200Hz相関0.859306、2268.03秒、要求との差+30ms | local sourceとprovider clockのずれを測定 |
| 構成 | 8 chronological cuts、406.55秒 | setup→変更→通知判明→謝罪→注意 |
| 字幕 | actual-audio faster-whisper small、手動固有語校正、142 cue | provider JSON3はdiscovery provenanceのみ |
| timing | 24 anchors、median 0ms、absolute p95 0ms、非発話表示0 | deterministic cut mappingの機械証明 |
| visual structure | creator-authored telop 4本、speech provenanceと分離 | episodeの段階を画面で追える |
| title | working 1案 + alternative 2案 | funeral/death hookを使わない |
| thumbnail rough | actual source frame、1280x720 + 320x180 | review補助。publication acceptance未判定 |
| media | H.264/AAC 1920x1080、405,217,162 bytes | full decode、A/V、音量、signal green |

working titleは
`Discordのプロフィールを遊びで変えたら、全スタッフに通知が飛んでいた`。
thumbnail roughの短文は`全スタッフに通知`。320x180でも主要文字を読めることを目視した。

## 検証と目視

全13 media checkがpass。duration 406.55秒、-14.93 LUFS、-1.85 dBTP、
隣接cut最大音量差0.82 LU、black/silence 0、full decode pass。
subtitle presentationは142 cue、3行超過・overlap・negative・orphan 0。
冒頭0.5秒は前置きだけを表示し、2.75秒の`Discordってさぁ使ってる`は英単語内で
折り返さない実フレームを確認した。終盤telopは
`変更は全体通知される`へ限定し、過剰な謝罪主体を主張しない。

review pageはtitle→thumbnail rough→videoの順で、page 200、MP4 Range 206 / 1024 bytes。
temporary serverは確認後に停止済み。

## 人間が閉じる判断

1. 6分46秒の因果と8 cutが、一話として自然に見えるか。
2. actual-audio字幕の語句・間・可読性に、公開品質へ向けた修正箇所があるか。
3. 4本のtelopが説明過多にならず、構成理解を助けるか。
4. working title / alternative 2案のpromiseが内容と一致するか。
5. source-frame thumbnail roughの焦点と短文が妥当か。

`accept`はこのSHAの内部editorial/language/title/rough scopeだけ。
`bounded_repair`は影響timestampとdimensionを限定した新identityを作る。
`reject`はv2を閉じる。いずれもrights、production、YPP、upload、publication、
visibilityを開かない。

## Git と再入

branch `codex/out14-push-microarc-editorial-v2`はexact base
`30b4891399ad474b624518f7dcb76591b68c8bef`から作成。
開始時fetch後の`origin/main`は`edb782a...7c7`で、baseはその1 commit先。
元v1 checkout、S1、Candidate 003/004/005、M2、M6はread-onlyで終了時再hash済み。
開始時のexact SHAとすべて一致し、両protected checkoutのtracked statusもclean。
push / PR / mergeはこのhandoffの権限外。

詳細な技術証跡と条件付き長期目標は
`docs/SUPERVISOR_STATUS_REPORT.md`、portable contractは
`docs/output_layer/OUT_14_PUSH_MICROARC_EDITORIAL_V2.md`。
