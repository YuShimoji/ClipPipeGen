---
id: project-context
title: Project Context - ClipPipeGen
type: durable_context
status: current
last_touched: 2026-08-25
current_slice: ED-13
phase: mixed_editorial_calibration_pass_whole_review_ready
active_branch: codex/wiki-tensaku-longform-family-v1
sync_observed_head: 51291010753563f038a5b4ae30d1b7c63dccf76d
upstream_parity: 2 0 after_two_local_calibration_commits_push_count_zero
health: EDITORIAL_CALIBRATION_PASS_335_WHOLE_REVIEW_READY_EP1_SOURCE_GATE_PARKED
---

# Project Context - ClipPipeGen

## 2026-08-25 mixed editorial calibration PASS

既存のhuman-accepted OUT-13 Candidate 005を、7 retained cut、1 exact duplicate DROP、
7 HOLD_REUSABLEへ再記述した。15 unitすべてがsource locator、観測と推論、Ruleまたは
case-specific判断、result mapping、限界へ接続され、15件のitem-level質問を再発行せずに
説明できる。共有文法は`Segment → Decision → Reason → Evidence → Rule → Override → Result`
だけであり、provider名、caption event、Clip固有cut IDはproject evidenceに留める。

この校正によりClipPipeGenのeditorial decision systemはproduction-scale entry `PASS`となった。
ただし別Missionなしに次動画やproductionを開始せず、rights/publicationも開かない。335.3秒
candidateは技術・構造判断を解消済みで、残るcreative authorityはwhole-candidateの
`accept / bounded revision`一件だけである。FrontierBoard Project 13にはGUI方向Choice 7が
すでにopenのため、競合Choiceは作らずreview readinessをtracked artifactへ記録した。

## 現在の軸

ClipPipeGenは、source acquisition、rights readback、編集authority、render、review、
publishing準備をepisode単位で接続する制作補助ツールである。現在のWiki添削familyは、
全配信規模を理解可能なEpisodeへ再構成するED-13にいる。

Episode 1「Wikiが作る人物像」のcanonical integrated cutは、CU-02
`youtube:Ocqg-RpQURY` 390–585秒のexact mediaと隣接receiptがないためfail-closedでpark中。
その代替として別素材を採用していない。一方、retained exact source
`youtube:1AcId5Yja10`では、ユーザーが選択した「話題が切り替わるところから始める」を
`clip-wiki-selected-opening-current-basis-v1-001`へ消費し、complete internal candidateを作成済みである。

## 最新のmaterial result

| 項目 | exact state | 意味 |
|---|---|---|
| successor package | `episodes/integrated_checklist_reverse_test_20260811/artifacts/cpg-integrated-checklist-reverse-test-v1/successors/cpg-wiki-selected-opening-current-basis-v1/package/` | Git外のcurrent internal candidate |
| exact media | 25,852,742 bytes / SHA `48c368b9ce5abf117114c29ba99f87a7a31973539aef0bb6aa34d246febff951` | full decode PASS、335.300秒container readback |
| selected opening | source 2530.319 / output 0.000 | Choice Set 4 revision 2を消費済み |
| endpoint | source 2865.599 | 次話題provider cue開始前。raw duration重複2.841秒をcurrent basisから除外 |
| current result | `INTERNAL_CANDIDATE_TECHNICALLY_COMPLETE_HUMAN_CONTENT_REVIEW_PENDING` | 技術完了とcontent acceptanceを分離 |

旧4本proofとportable manifestは選択根拠のhistoryとして不変。current authorityは新successorであり、
openingとendpointを一問へ束ねる旧decision requestへ戻さない。

2.841秒のendpoint失敗は
[`clip_real_decision_case_v1.json`](output_layer/clip_real_decision_case_v1.json)へ実証拠として固定した。
旧endpoint proofのoutput 13.119–15.960秒と、current candidateから外したsource
2865.599–2868.440秒を同じcaseで追える。後者はDROPではなく、次話題のcontextとして再利用可能な
HOLDである。Rule修正はproposalで、ユーザーの明示文はChoice Set 6のcandidate固有権限にだけ使う。

whole-video校正は
[`clip_full_video_editorial_calibration_v1.json`](output_layer/clip_full_video_editorial_calibration_v1.json)
に固定した。335.3秒を8 decision unitへ分け、各unitでKEEP理由、observed/inferred、Ruleまたは
case-specific judgment、confidence、limitation、result、隣接関係を追える。8 unitはcurrent editへ
含まれるという意味のKEEPであり、human acceptanceではない。source内の実編集cutは1、DROPは0、
endpoint外2.841秒はHOLD_REUSABLEである。

opening・endpoint・8件のunit採否・字幕timingの計11問は追加Choiceなしで既存authority/evidenceへ
圧縮できた。残るhuman authorityはwhole-candidate content acceptance一件。現行packageの
timeline 97 caption参照とreadback 96 itemsの差（dangling `caption_0097`）はLOCAL REPAIRとして
記録し、packageは改変せずfuture builderだけを修復した。このためproduction-scale判定はPARTIALで、
既存multi-cut artifactを使うもう一回の校正が必要である。

## 現在のgapと境界

- opening 2530.319はユーザー選択済み。current candidateの切り取り位置も明示的に妥当とされたため、再pollしない。
- provider event_001639のraw durationをsemantic completionへ昇格しない。normalized display endと
  次話題event_001641 startが同じ2865.599であることをcurrent endpoint contractとする。
- 字幕timing、改行、幅、burn-in、full decodeはtechnical evidenceであり、human content acceptanceではない。
- 親338.166016秒のfull-1x review queueは別gateで、短尺proofでは代替・再pollしない。
- rights、production subtitle/design/render、delivery、publication、monetization、uploadは未承認。
- Episode 1のCU-02 exact-source gateは、このindependent proofによって解消した扱いにしない。

## 別端末での最短再開

1. `README.md` → `docs/RUNTIME_STATE.md` → `docs/CURRENT_HANDOFF.md`を読む。
2. Gitのbranch / HEAD / upstream parityと`git ls-files episodes`が0件であることを確認する。
3. 親CoordinatorからClipPipeGen portable ZIPと外部manifestを受け取り、manifest記載のSHA、
   member count、relative pathsを検証する。Git cloneだけではreview mediaは得られない。
4. successor MP4/receiptをportable media resolverへ登録し、FrontierBoardでexact size/SHAを確認する。
5. DecisionCaseで旧推論、Rule proposal、Human Override、335.3秒resultを読み、必要ならcontent全体のbounded revisionだけをexact MP4 SHAへbindする。

## 次の依存順

`full-video calibration readback -> existing mixed KEEP/DROP/HOLD artifactで一回再校正 ->
必要ならwhole-candidate content review一件`
がcurrent laneの最短経路である。
Episode 1本線は独立して`Ocqg-RpQURY exact bytes + receipt -> preflight rerun -> integrated render`。
どちらからもrights、production、publicationを推定しない。
