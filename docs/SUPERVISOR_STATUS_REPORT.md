# 監修AI向け現状報告 — 2026-07-23 OUT-13同期・開発準備・長期目標

更新日: 2026-07-23 JST

## 結論と監修上の現在地

リモートの最新状態は安全に取り込み済みで、現在のcheckoutは開発を継続できる。active branch
`codex/out-13-editorial-video-candidate-v1`は`git pull --ff-only`により`c1566b3`から`2d8c4d6`へ
fast-forwardし、同期時点で追跡先とのparityは`0 0`だった。integration正本の`main` / `origin/main`は
`5d6f69a`で一致し、同期起点`2d8c4d6`はmainより3 commit先である。本報告commitをpushするとactive
branchはmainより4 commit先になるが、OUT-13をmainへmergeした事実はまだない。

OUT-13のコードだけでなく、同一マシンのexact review artifactも利用可能である。前版報告は別時点の
存在確認からplan/package不在としていたが、今回の再計測では`editorial_plan_input.json`、25-fileの
review package、73,776,611-byteの`final_video.mp4`が存在する。final SHAはtracked contractの
`84ed7aa6fc7aa1d478d7fa8f8783e349a5ffa56a7a59dc49c30daafa0791d7e2`と一致し、`--resume`は
0.281秒、再レンダーなし、同一manifest SHAを返した。review pageはHTTP 200、動画byte rangeは206を
再確認した。従って現在の最短bottleneckはartifact回収ではなく、この一本に対する人間の編集判断である。

## リモート同期とbranch topology

| 確認面 | 2026-07-23の実測 | 監修上の意味 |
|---|---|---|
| fetch | `origin/codex/out-13-editorial-video-candidate-v1`が`c1566b3..2d8c4d6`へ更新 | remote refsを最新化 |
| pull | current branchを`git pull --ff-only`で1 commit fast-forward | merge commit、履歴改変、user差分の退避なし |
| integration baseline | local `main` / `origin/main` = `5d6f69a` | OUT-12までのcanonical main |
| active sync baseline | `2d8c4d6`; tracking parity `0 0` | OUT-13実装と前版handoffを取得済み |
| mainとの差 | `origin/main...2d8c4d6` = `0 3` | active branchだけが3 commit先、main側の未取込commitなし |
| public hygiene | `git ls-files episodes` = 0 | source・生成mediaをpublic Gitへ入れていない |

今回取り込んだ`2d8c4d6`は監修報告、project context、decision/idea ledger、artifact registryの更新だった。
実装本体のverified headは`c1566b3`のままだが、その後のtracked handoffを含めてcurrent branchを
`2d8c4d6`まで同期した。main統合、人間受理、rights、production/public acceptanceはこの同期からは
発生しない。

## 開発可能性の再構築と検証

| 面 | 実行結果 | 開発workflowへの効果 |
|---|---|---|
| JavaScript依存 | `npm ci`成功、23 packages追加、24 packages audit、脆弱性0 | lockfile準拠でElectron環境を再構築 |
| dependency tree | `npm ls --depth=0` → Electron 42.0.0 | 欠落・extraneous依存なし |
| Python runtime | CPython 3.11.0、uv/uvx 0.10.0、Pillow 12.3.0 | 現checkoutで使った再現可能なtest/runtime値を固定 |
| full suite | `uvx --with Pillow pytest -q` → 606 passed / 65.37s | OUT-13を含む全suiteに回帰なし |
| GUI | `npm run smoke` → `gui smoke: OK` | Node側operator surfaceが起動可能 |
| Electron | `npm run smoke:electron` → `electron smoke: OK` | desktop entrypointとElectron binaryを利用可能 |
| CLI | `build-editorial-video-candidate --help`成功 | 必須input、resume/force、review portを解決 |
| media toolchain | FFmpeg/ffprobe 8.1.1、yt-dlp 2026.03.17 | source取得・probe・internal render経路のtoolingあり |
| exact resume | 0.281s、`render_executed=false`、video/manifest SHA不変 | stale cacheを混ぜず高コストrenderをskip |
| review serving | page 200、`final_video.mp4` Range 206 / 1,024 bytes | launcher後にseek可能なreview surfaceを提供 |

テスト前後でtracked/staged/untracked差分はなく、依存整備による変更はignored `node_modules`と通常の
Python/test cacheに限られた。`episodes/`には512 local filesがあるがGit追跡は0件である。cleanup policyの
保護対象R3 `human_preview_session`は34 files / 60,060,797 bytesで存在し、OUT-13を含むsource-derived
evidenceとともに削除していない。active previewを巻き込む`git clean -fdX`等の広範cleanは行っていない。

## OUT-13の到達点とlive artifact

| 面 | このcheckoutの確定値 | 判断できること |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-001`; `EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1` | plan/media/evidence/reviewのidentityが一つ |
| source | `youtube:7J5aS_pcBj4`; SHA `e2206cef...2d18`; 164.768798s; 1920x1080 | 既存official sourceを利用、新規取得なし |
| plan input | `episodes/out13_editorial_video_candidate_20260722/editorial_plan_input.json`; 11,333 bytes; SHA `75289fba...cb2b` | 選択・除外authorityを同一マシンで再利用可能 |
| editorial plan | 6 chronological cuts / 4 sections / 6 omitted spans / utilization 74.542% / mapping 1.0 | 何を残し何を落としたかをcut単位で監査可能 |
| final MP4 | 122.866016s; H.264 High/AAC; 1920x1080; 73,776,611 bytes; SHA `84ed7aa6...791d7e2` | 人間判断をbindすべきexact identity |
| subtitles | official JA JSON3 77 cue; Keifont 100px; max 2 lines; overflow/overlap/negative/orphan 0 | timingとpresentationを同じ動画で確認可能 |
| audio/signal | -14.61 LUFS; -1.58 dBTP; max adjacent delta 0.94 LU; black/silence event 0 | internal machine QA pass、production mix承認ではない |
| package | 25 files / 78,180,658 bytes; manifest self SHA `8f0be672...02e8` | review page、readback、contact sheet、waveformを一入口で監査可能 |
| validation | 19 review-visible checks pass、page 200 / MP4 Range 206 | 技術欠陥をhuman editorial reviewから分離 |
| resume | fingerprint `051832b9...e3d8`; 0.281s; renderなし | exact artifactを壊さず再開可能 |

同一マシンの入口は次である。launcherはforeground serverを起動し、終了はそのPowerShellで`Ctrl+C`を使う。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out13_editorial_video_candidate_20260722\review\out13_editorial_video_candidate\review\open_preview.ps1
```

URLは`http://127.0.0.1:8076/review/index.html`。artifactはignored `episodes/`配下のlocal retained evidenceで
あり、Gitだけでは別cloneへ移らない。remoteでportableなのはbuilder、tests、docs、hash/manifest contractまで。
このlocal availabilityを別hostにも一般化せず、別hostでは`Test-Path`とhash確認後だけlauncherを案内する。

## 現在の判断packet

次の判断はOUT-13 exact MP4一本に対するinternal editorial reviewである。reviewerは動画を通して見たうえで、
次の四軸を一つのreceiptにまとめる。

| 判断軸 | 確認内容 | 結果に必要な粒度 |
|---|---|---|
| 編集構成 | 6 cut / 4 sectionの順序、間、除外、終端が自然か | accept、または該当cut/timeと欠陥 |
| 字幕presentation | 可読性、2行wrap、短時間cue、二重表示、safe area | accept、またはcue/timeと修正方向 |
| 画面 | source-native frame、cut境界、black/frame異常、視認性 | accept、またはframe/timeと症状 |
| 音声 | cut前後の連続性、音量差、途切れ、聞き取り | accept、またはcut/timeと症状 |

結果はexact final SHAへbindした`accept`、理由と対象を限定した`bounded repair`、または`reject`のいずれか。
人間判断を未入力のままAgentが代筆しない。受理されてもrights、production subtitle/design/render、thumbnail、
public/publishing、uploadへ自動昇格させない。

## 受入監査と残る不確実性

| 区分 | 現在判定 | 次に必要なこと |
|---|---|---|
| OUT-13 code must-fix | なし | 606 tests、CLI/GUI smoke、exact resumeを維持 |
| review access must-fix | 解消 | plan、final、review page、HTTP Rangeが同一マシンで利用可能 |
| human editorial acceptance | 未完了 | exact SHAに対する人間のaccept/repair/reject |
| main integration | 未実施 | editorial closure後にmerge preflightとmain回帰を行う |
| rights | pending | source/rangeと時点を持つrights owner receipt |
| production subtitle/render | false | design/QC仕様を別gateとして承認・検証 |
| thumbnail/publishing/upload | 未着手またはclosed | upstream gateが閉じた後に別sliceで扱う |
| portability | local packageは非portable | 必要時のみprivate transport/retention/ACLを明示承認 |
| route generality | OUT-12 second-source repeatability debtあり | 3分以上distinct sourceでOUT-12 routeを独立再検証 |

前版のartifact不在はこのcheckoutでは解消したが、動画内容の良否はまだ人間が判断していない。machine QAと
review accessの成功を編集受理へ読み替えないことが最大の残存不確実性である。

## 可能な限り先まで見通した目標案

以下は依存関係を保つためのgoal ladderであり、rights・credential・公開操作への着手承認ではない。

| 段階 | 目的とworkflow効果 | 着手条件 | 完了を示す最小証拠 | 現在状態 / owner |
|---|---|---|---|---|
| M0: sync + dev readiness | remote、依存、testsを同じ基準へ戻す | current repo | parity、606 tests、GUI/CLI smoke、tracked episodes 0 | 完了 / Agent |
| M1: exact local review readiness | humanが探索せず同じbytesを見られるようにする | local plan/package | final/manifest hash、resume、single open command、200/206 | 完了 / Agent |
| M2: internal editorial decision | composition/subtitle/picture/audioのconsumer判断を閉じる | M1 | exact SHA-bound accept/repair/reject receipt | pending / Human reviewer |
| M3: bounded editorial closure | 指摘箇所だけを直し修復loopを無制限化しない | M2がrepairなら対象明示。acceptならskip | one bounded rerender、19 checks、lineage、再review | conditional / Agent + Human |
| M4: main integration | 未mergesliceをportableなintegration正本へ戻す | M2/M3 closure、clean preflight | main merge、full suite、docs一致、origin parity | not started / Agent |
| M5a: rights clearance | 技術成功と利用許可を接続する | source/range、guideline snapshot、rights owner | allow/deny/restriction、時点、reviewer receipt | pending / Rights owner |
| M5b: production subtitle design | font/license、line break、safe area、speaker表現を制作判断へ上げる | editorial accept、design owner | exact visual receipt、font/license readback、適用範囲 | closed / Human designer |
| M5c: production render acceptance | internal MP4をdelivery仕様へ上げる | delivery profile、device/color/audio QC | full decode、device QA、exact SHA、human production receipt | closed / Supervisor/User |
| M6: episode candidate convergence | M5a-cの独立結果を一identityへ束ねる | 各receipt | gateを混同しないepisode manifestとlineage | proposed / Agent + Supervisor |
| M7: route generality | OUT-12をdistinct long sourceでも再現できると示す | M4、別の3分以上source、同じroute contract | second-source build/validation/resumeと差分scorecard | debt / Agent |
| M8: thumbnail + metadata | video確定後の手戻りを減らす | M6、3〜5 accepted output、thumbnail再開判断 | reproducible cover contract、exact acceptance、metadata draft | parked/proposed / Human + Agent |
| M9: private/unlisted delivery | 公開せずOAuth/idempotency/rollbackを証明する | M5-M8、credentials明示承認 | dry-run、private/unlisted ID、visibility/thumbnail receipt、retry/rollback | 未実装・要承認 / Human owner |
| M10: explicit public release | 公開判断を監査可能に閉じる | M9、全owner receipt | pre-public packet、visibility/made-for-kids明示、公開後receipt | future gate / Human owner |
| M11: multi-episode operations | 単発成功をqueue/retry/retention運用へ上げる | M4-M10 contract安定、複数episode evidence | failure isolation、observability、retention、operator cockpit | long-range proposal / Agent + Operator |
| M12: quality feedback loop | human判断を次episodeの改善に再利用する | M11、複数の理由付きreceipt | defect taxonomy、trend、regression fixture、再発率readback | long-range proposal / Supervisor + Agent |

critical pathは`M2 -> M3（必要時） -> M4 -> {M5a, M5b, M5c} -> M6 -> M8 -> M9 -> M10 -> M11 -> M12`。
M5a-cは並行準備できるが、一つのpassを他の承認に代用しない。M7はpublic routeの前提ではないが、単一source
最適化のriskを下げる独立監査としてM4後に差し込める。

## 次に推奨する四つの入口

| 入口 | いま減らす摩擦 | 選ぶと次に可能になること |
|---|---|---|
| **Review — M2** | machine passのまま人間判断が空いている | editorial acceptance、または具体的なbounded repair scopeを得る |
| **Audit — M3準備** | repair条件が曖昧なままレビュー結果を待つrisk | 指摘時に一回のsource-specific修復へ直行できる |
| **Verify — M7** | OUT-12が一sourceでしか実証されていない | 長尺routeのgeneralityとsource-specific仮定を分離できる |
| **Advance — M5a** | 技術artifactと利用許可が分離している | editorial accept後、production候補へ進めるrangeを確定できる |

第一推奨は`Review — M2`。artifactはすでに同一マシンで開けるため、新しい実装や回収を挟まず、人間判断を
exact SHAへbindするのが最短である。レビュー待ちの間に進めるなら`Audit — M3準備`が最もscope逸脱が少ない。

## 監修AIが維持する境界

- integration正本`main`とactive OUT-13 branchを区別し、未mergeをmergedと報告しない。
- local artifact実在とcross-machine portabilityを分け、`episodes/`をtrackしない。
- machine validation、automation acceptance、human editorial acceptanceを相互代用しない。
- OUT-13の人間判断を代筆せず、accept/repair/rejectをexact SHAへbindする。
- rights、production subtitle/design/render、thumbnail、public/publishing/uploadを一括で開かない。
- NLMYTGenを含む他repositoryを読まず、source textからspeaker、歌唱、歌詞、rightsを追加推定しない。
