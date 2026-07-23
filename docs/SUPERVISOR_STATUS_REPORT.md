# 監修AI向け現状報告 — 2026-07-23 OUT-13最新同期・開発準備・長期目標

更新日: 2026-07-23 JST

> **現状注記（2026-07-24）:** 本報告の OUT-13 current-state claim は superseded。
> 現在の正本は [CURRENT_HANDOFF.md](CURRENT_HANDOFF.md) と [RUNTIME_STATE.md](RUNTIME_STATE.md)。

## 結論と監修上の現在地

リモートの最新変更は安全に取り込み済みで、コード開発は継続できる。active branch
`codex/out-13-editorial-video-candidate-v1`を`2d8c4d6`から`558f681`へ
`git pull --ff-only`で1 commit進め、同期直後のupstream parityは`0 0`だった。
integration正本の`main` / `origin/main`は`5d6f69a`で一致し、同期baseline `558f681`は
mainより4 commit先である。OUT-13をmainへmergeした事実はなく、本報告commitが次のremote
handoff tipになる。

依存、606件のPython test、Node/Electron smoke、OUT-13 CLI helpはすべてpassした。一方、今回
取り込んだ`558f681`が記録する「このcheckoutにOUT-13 exact packageがあり、即human review可能」
というhost-local事実は、同期後のlive filesystemとSHA照合では再現しなかった。
`editorial_plan_input.json`、OUT-13 output directory、final MP4、readback、launcherは同一repository
配下に存在しない。さらにlocal source、transcript、rights snapshotはtracked OUT-13契約のSHAと
一致せず、official JA captionだけが一致する。従って、現在の正確な状態は次の二つに分かれる。

- tracked code/docs/testsとOUT-13のsource-host machine receiptは利用可能で、実装修正・監査・testは継続可能。
- exact OUT-13 MP4の再視聴とhuman editorial decisionは、exact package/input setの復旧、または新identityでの明示的rebuildまで進めない。

OUT-13 laneの進捗を「implementation → exact access → human decision → bounded closure → main integration」
の5 gateで測ると、現在は`[████░░░░░░] 40%`。implementationと開発環境は完了し、exact access以降が
未完了である。これは製品全体や公開準備の完成率ではない。

## リモート同期とbranch topology

| 確認面 | 2026-07-23の実測 | 監修上の意味 |
|---|---|---|
| fetch | remote OUT-13 branchが`2d8c4d6..558f681`へ更新 | remote refsを最新化 |
| pull | current branchを`git pull --ff-only origin codex/out-13-editorial-video-candidate-v1`で1 commit fast-forward | merge commit、履歴改変、user差分の退避なし |
| integration baseline | local `main` / `origin/main` = `5d6f69a`、parity `0 0` | OUT-12までのcanonical main |
| active sync baseline | `558f681`、tracking parity `0 0` | OUT-13実装と最新remote handoffを取得 |
| mainとの差 | `main...558f681` = `0 4` | active branchだけが4 commit先 |
| public hygiene | `git ls-files episodes` = 0 | source・生成mediaをpublic Gitへ入れていない |

取り込んだ`558f681`は10 tracked filesのdocs/dashboard更新で、実装headは`c1566b3`のままである。
同期によってmain統合、人間受理、rights、production/public acceptanceは発生しない。remote handoffの
local-availability claimはportable事実ではなく、今回のlive readbackでsupersedeする。

## 開発可能性の再検証

| 面 | 実行結果 | 開発workflowへの効果 |
|---|---|---|
| JavaScript依存 | `npm ci`成功、23 packages追加、24 packages audit、脆弱性0 | lockfile準拠でElectron環境を再構築 |
| dependency tree | `npm ls --depth=0` → Electron 42.0.0 | 欠落・extraneous依存なし |
| Node runtime | Node 24.13.0、npm 11.6.2 | 現端末のdesktop開発runtimeを明記 |
| Python runtime | CPython 3.13.3、uv/uvx 0.10.7、Pillow 12.3.0 | 現checkoutで使ったtest/runtimeを固定 |
| full suite | final `uvx --with Pillow pytest -q` → 606 passed / 68.84s | OUT-13を含む全suiteに回帰なし |
| GUI | `npm run smoke` → `gui smoke: OK` | Node側operator surfaceが起動可能 |
| Electron | `npm run smoke:electron` → `electron smoke: OK` | Electron binary取得後もdesktop entrypointが起動可能 |
| CLI | `build-editorial-video-candidate --help`成功 | source/plan/transcript/caption/rights、resume/force引数を解決 |
| media toolchain | FFmpeg/ffprobe 8.0.1、yt-dlp 2026.03.17 | exact input setまたはnew rebuild planが揃えばrender経路を利用可能 |
| predecessor | OUT-12 final MP4 142,789,781 bytes、SHA `5d391ffd...a584`一致 | operational predecessorはsame-machineで再検査可能 |

テスト前後でtracked/staged/untracked差分はなく、依存整備による変化はignored `node_modules`と通常の
cacheに限られた。`episodes/`は933 local files、Git追跡0件。cleanup policyの保護対象R3
`human_preview_session`は28 files / 33,712,427 bytesで存在し、削除していない。
active previewやignored mediaを巻き込むbroad cleanupは行っていない。

## OUT-13のportable実装契約とsource-host receipt

次の値はtracked source-host receiptであり、現在のcheckoutでlive mediaを再計測した値ではない。

| 面 | tracked receipt | 判断できること |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-001`; `EDITORIAL_REPRESENTATIVE_VIDEO_REVIEWABLE_V1` | plan/media/evidence/reviewのhistorical identity |
| source | `youtube:7J5aS_pcBj4`; SHA `e2206cef...2d18`; 164.768798s; 1920x1080 | original buildがbindしたsource bytes |
| editorial plan | 6 chronological cuts / 4 sections / 6 omitted spans / utilization 74.542% / mapping 1.0 | 何を残し何を落としたかのcontract |
| final MP4 | 122.866016s; H.264 High/AAC; 1920x1080; 73,776,611 bytes; SHA `84ed7aa6...791d7e2` | human reviewをbindすべきexact historical identity |
| subtitles | official JA JSON3 77 cue; Keifont 100px; max 2 lines; overflow/overlap/negative/orphan 0 | caption timing/presentationのmachine receipt |
| audio/signal | -14.61 LUFS; -1.58 dBTP; max adjacent delta 0.94 LU; black/silence event 0 | internal machine QA pass、production mix承認ではない |
| validation | 19 review-visible checks pass、source-host page 200 / MP4 Range 206 | original packageがreviewableだった証拠 |
| resume | source-host 0.281s、renderなし、video/manifest SHA不変 | original fingerprintのfail-closed receipt |

成立済みなのはOUT-13 codeとsource-host reviewable artifact receiptであり、現checkoutからのreview
accessではない。rights、production subtitle/design/render、thumbnail、winner、public/publishing、
uploadも引き続き未承認である。

## 現checkoutのartifact・input監査

| 対象 | tracked OUT-13契約 | live checkout | 結論 |
|---|---|---|---|
| source MP4 | SHA `e2206cef...2d18` | 35,281,366 bytes、SHA `6f78657e...6103a` | bytes不一致。exact build inputではない |
| transcript | SHA `ef928d4e...b42d6` | 43,369 bytes、SHA `4a7b4fd8...3495` | bytes不一致 |
| official JA caption | SHA `3c15535f...d169919` | 40,303 bytes、同じSHA | 一致 |
| rights snapshot | SHA `e6ea9471...64c12` | 2,347 bytes、SHA `4302c4a1...bb8` | bytes不一致 |
| editorial plan input | 11,333 bytes、documented SHA `75289fba...cb2b` | 不在 | exact resume/rebuild不可 |
| final/review package | 25 files / 78,180,658 bytes、final SHA `84ed7aa6...791d7e2` | directoryごと不在 | launcher、HTTP 200/206、human review不可 |

targeted searchはrepository rootと配下worktreeに限定し、`editorial_plan_input.json`、OUT-13 directory、
OUT-13 final/readback/launcherを発見しなかった。他repositoryは読んでいない。

この差分は「同じYouTube identityだから同じinput」とは扱えない。local source/transcript/rightsと
tracked rangesから再生成する場合は、旧artifactを復元したと主張せず、新しいplan payload hash、
input fingerprint、artifact ID、final SHA、lineageを持つnew identityにする。

## 現在の判断packet

human editorial reviewの問い自体は変わらない。exact MP4一本について、編集構成、
caption presentation、画面、音声を確認し、`accept`、対象を限定した`bounded repair`、
または`reject`をfinal SHAへbindする。ただし現checkoutではその前提artifactがないため、
先に次の二経路のどちらかをownerが選ぶ。

| 経路 | 目的 | 必要条件 | 効果とtradeoff |
|---|---|---|---|
| exact recovery | original `84ed7aa6...791d7e2`をそのままreviewする | 生成host、承認済みprivate transport、manifest/hash照合、保持/削除方針 | original identityへ最短で判断できる。外部調整とprivate artifact扱いが必要 |
| new-identity rebuild | currentまたは再取得したinputsからreviewable successorを作る | source/input authority、plan再作成、旧receiptとの非同一性明示 | この端末だけで前進可能。旧SHAへのreviewではなく新artifactへの判断になる |

どちらも選ばずにhuman decisionを代筆しない。exact recoveryのtransportやnew input取得に
credentials/OAuth/paymentが必要なら、実行前にowner gateを開く。

## 受入監査と残る不確実性

| 区分 | 現在判定 | 次に必要なこと |
|---|---|---|
| OUT-13 code must-fix | なし | 606 tests、CLI/GUI smokeを維持 |
| development readiness | green | branch parity、依存、toolchain、worktree hygieneを維持 |
| exact human-review access | blocked | exact recoveryまたはnew-identity rebuildを明示選択 |
| human editorial acceptance | 未完了 | reviewable exact bytesに対するhuman receipt |
| main integration | 未実施 | editorial closure後にmerge preflightとmain回帰 |
| rights | pending | source/rangeと時点を持つrights owner receipt |
| production subtitle/render | false | design/QC仕様を別gateとして承認・検証 |
| portability | code/docsのみportable | media transport/retention/ACLはowner判断 |
| route generality | OUT-12 second-source debtあり | distinct 3分以上sourceで独立再検証 |

最大の残存不確実性は、source-host receiptの成功と現checkoutのartifact不在を混同しやすいこと。
machine QA、local availability、human acceptance、rights、production/public gateを相互代用しない。

## 可能な限り先まで見通した目標案

以下は依存関係を保つためのgoal ladderであり、rights・credentials・private transport・公開操作への
着手承認ではない。

| 段階 | 目的とworkflow効果 | 着手条件 | 完了を示す最小証拠 | 現在状態 / owner |
|---|---|---|---|---|
| M0: sync + dev readiness | remote、依存、testsを同じ基準へ戻す | current repo | parity、606 tests、GUI/CLI smoke、tracked episodes 0 | 完了 / Agent |
| M1: OUT-13 implementation baseline | explicit plan→editorial MP4→reviewのportable code contractを成立させる | OUT-12 operational | source-host receipt、tracked builder/tests/docs | 完了 / Agent |
| M2: artifact identity recovery | humanがreview可能なsame bytesへ到達する | exact transportまたはnew rebuild authority | package/input/plan hash、single launcher、availability receipt | blocked / Human owner + Agent |
| M3: internal editorial decision | composition/subtitle/picture/audioのconsumer判断を閉じる | M2 | exact final SHA-bound accept/repair/reject | pending / Human reviewer |
| M4: bounded editorial closure | 指摘箇所だけを直しrepair loopを無制限化しない | M3がrepairなら対象明示。acceptならskip | one bounded rerender、19 checks、lineage、再review | conditional / Agent + Human |
| M5: main integration | 未merge sliceをportable integration正本へ戻す | M3/M4 closure、clean preflight | main merge、full suite、docs/dashboard一致、origin parity | not started / Agent |
| M6a: rights clearance | 技術成功と利用許可を接続する | source/range、guideline snapshot、rights owner | allow/deny/restriction、時点、reviewer receipt | pending / Rights owner |
| M6b: production subtitle design | font/license、line break、safe area、speaker表現を制作判断へ上げる | editorial accept、design owner | exact visual receipt、font/license readback、適用範囲 | closed / Human designer |
| M6c: production render acceptance | internal MP4をdelivery仕様へ上げる | delivery profile、device/color/audio QC | full decode、device QA、exact SHA、human production receipt | closed / Supervisor/User |
| M7: route generality | OUT-12をdistinct long sourceでも再現できると示す | M5、別の3分以上source、同じroute contract | second-source build/validation/resumeと差分scorecard | debt / Agent |
| M8: episode candidate convergence | M6a-cの独立結果を一identityへ束ねる | 各receipt | gateを混同しないepisode manifestとlineage | proposed / Agent + Supervisor |
| M9: thumbnail + metadata | video確定後の手戻りを減らす | M8、3〜5 accepted output、thumbnail再開判断 | reproducible cover contract、exact acceptance、metadata draft | parked/proposed / Human + Agent |
| M10: private/unlisted delivery | public化せずOAuth/idempotency/rollbackを証明する | M6-M9、credentials明示承認 | dry-run、private/unlisted ID、visibility/thumbnail receipt、retry/rollback | 未実装・要承認 / Human owner |
| M11: explicit public release | 公開判断を監査可能に閉じる | M10、全owner receipt | pre-public packet、visibility/made-for-kids明示、公開後receipt | future gate / Human owner |
| M12: multi-episode operations | 単発成功をqueue/retry/retention運用へ上げる | M5-M11 contract安定、複数episode evidence | failure isolation、observability、retention、operator cockpit | long-range proposal / Agent + Operator |
| M13: quality feedback loop | human判断を次episodeの改善に再利用する | M12、複数の理由付きreceipt | defect taxonomy、trend、regression fixture、再発率readback | long-range proposal / Supervisor + Agent |

critical pathは`M2 -> M3 -> M4（必要時） -> M5 -> {M6a, M6b, M6c} -> M8 -> M9 -> M10 ->
M11 -> M12 -> M13`。M6a-cは並行準備できるが、一つのpassを他の承認に代用しない。M7はpublic
routeの前提ではないが、単一source最適化のriskを下げる独立監査としてM5後に差し込める。

## 次に推奨する四つの入口

| 入口 | いま減らす摩擦 | 選ぶと次に可能になること |
|---|---|---|
| **Restore — M2 exact** | original MP4/plan/input setがこのcheckoutにない | original SHAへ最短でhuman decisionをbindできる |
| **Rebuild — M2 successor** | private transportなしでは停止すること | new identityとしてreview surfaceを自力で再構成できる |
| **Audit — M4準備** | recovery待ちで実装が止まること | plan/failure/resume/corrective-pass境界を先に固められる |
| **Verify — M7準備** | OUT-12が一sourceでしか実証されていない | main統合後のsecond-source generality sliceを短く開始できる |

第一推奨は`Restore — M2 exact`。original packageへ到達できない、またはprivate transportを
選ばない場合は`Rebuild — M2 successor`へ明示的に切り替える。review accessを待つ間に進めるなら
`Audit — M4準備`が最もscope逸脱が少ない。

## 監修AIが維持する境界

- integration正本`main`とactive OUT-13 branchを区別し、未mergeをmergedと報告しない。
- source-host receipt、current local availability、human editorial acceptanceを相互代用しない。
- local source identity名が同じでもSHA不一致を同一bytesと扱わない。
- `episodes/`をtrackせず、local media、`.serena`、他worktree、credentialsを保護する。
- OUT-13の人間判断を代筆せず、accept/repair/rejectをreviewed final SHAへbindする。
- rights、production subtitle/design/render、thumbnail、public/publishing/uploadを一括で開かない。
- NLMYTGenを含む他repositoryを読まず、source textからspeaker、歌唱、歌詞、rightsを追加推定しない。
