# 監修AI向け現状報告 — 2026-07-22 OUT-13 remote sync / development readiness / long-range goals

更新日: 2026-07-22 JST

## まず押さえる現在地

リモート同期と開発準備は完了した。`main`は`8faaab2`から`5d6f69a`へff-onlyで更新し、同時に検出した
OUT-13 remote branchをlocal tracking branchとして再開した。現在のcheckoutは
`codex/out-13-editorial-video-candidate-v1`、検証対象implementation headは`c1566b3`、同期時のupstream
parityは`0 0`である。本報告commitがpush後のremote handoff tipになる。
`main`より2 commit先だが、mainへのmergeやhuman editorial acceptanceはまだ行っていない。

OUT-13は、明示的なcaption/transcript evidence付きeditorial planから6つの非連続cutを選び、
Keifont字幕、実MP4、19項目validation、video-first review packageまで生成する実装である。remote code、
tests、契約は取得済みで、このcheckoutでは606 testsとGUI/CLI smokeがpassしたため開発は継続できる。

ただし、このroot checkoutにはOUT-13のsource/transcript/caption/rights入力はある一方、
`editorial_plan_input.json`とsource-host生成packageがない。従って、source-hostで記録されたexact MP4
SHA `84ed7aa6...791d7e2`をこの場で再生してhuman decisionへ進むことはできない。これはコードの
development blockerではなく、current human-review gateだけのartifact-access blockerである。

## リモート同期とbranch topology

| 確認面 | ライブ結果 | 監修上の意味 |
|---|---|---|
| fetch | `origin/main`が`8faaab2..5d6f69a`へ進み、OUT-13 branchを新規検出 | remote refsを最新化 |
| main pull | `git pull --ff-only origin main`で2 commitをfast-forward | merge commitや履歴改変なし |
| integration branch | `main` / `origin/main` = `5d6f69a` | OUT-12までのcanonical integration baseline |
| active development branch | verified implementation `c1566b3`; report tipは本commit | OUT-13 code/docs/testsを含む未merge review branch |
| branch distance | `main...OUT-13` = `0 2` | OUT-13だけが2 commit先、main側の未取込commitなし |
| upstream parity | active branch `0 0` | local branchとremote branchは一致 |
| public hygiene | tracked `episodes/` 0件 | source/生成mediaをpublic Gitへ入れていない |

今回のpullで入った`main`側2 commitは、旧OUT-12監修報告、artifact registry、goal ledgerの更新だった。
その直後にremote OUT-13実装が作られていたため、旧報告の「M1 second-source repeatabilityが次」は
current development laneとずれていた。本報告とcockpit更新は、そのdriftをOUT-13 human consumer中心へ
再アンカーする。

## 開発可能性の検証

| 面 | 実行結果 | 効果 |
|---|---|---|
| JavaScript依存 | `npm ci`成功、23 packages追加、24 packages audit、脆弱性0 | lockfile準拠のElectron環境を再構築 |
| dependency tree | `npm ls --depth=0`でElectron 42.0.0 | 欠落・extraneous依存なし |
| Python | uv Python 3.13.3、uv/uvx 0.10.7 | Pillow込みの再現可能なtest runtime |
| full suite | `uvx --with Pillow pytest -q` → 606 passed / 147.15s | OUT-13専用testを含む全suite pass |
| GUI | `npm run smoke` → `gui smoke: OK` | Node側のoperator surfaceが起動可能 |
| Electron | `npm run smoke:electron` → `electron smoke: OK` | desktop runtime入口が起動可能 |
| CLI | `build-editorial-video-candidate --help`成功 | source/plan/transcript/caption/rights、resume/force引数を解決 |
| media toolchain | FFmpeg/ffprobe 8.0.1、yt-dlp 2026.03.17 | 必要入力が揃えばlocal render/rebuild可能 |
| worktree | 開始時tracked/staged/untracked変更0 | user-owned tracked作業を上書きしていない |

ignored rootには`_tmp`、`.pytest_cache`、`.ruff_cache`、`.serena`、`episodes`、`node_modules`がある。
`node_modules`は今回の開発依存、`episodes`はsource-derived evidence、`.serena`と`_tmp`は既存local stateとして
保持した。cleanup policyの保護対象R3 `human_preview_session`も28 files / 33,712,427 bytesで存在する。
active previewやignored mediaを消すbroad cleanupは行っていない。

## OUT-13の実装到達点

tracked contractが記録するsource-host実績は次の通り。ここにあるmedia値はremote branchの
machine readback由来であり、このroot checkoutでの再計測ではない。

| 面 | source-hostの確定値 | 判断できること |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-001` | plan/media/evidence/reviewのidentity |
| source | `youtube:7J5aS_pcBj4`; SHA `e2206cef...2d18`; 164.768798s; 1920x1080 | 既存official sourceを利用、新規取得なし |
| editorial plan | 6 chronological cuts / 4 sections / 6 omitted spans / utilization 74.542% / mapping 1.0 | 何を残し何を落としたかをcut単位で監査可能 |
| final MP4 | 122.866016s; H.264/AAC; 73,776,611 bytes; SHA `84ed7aa6...791d7e2` | human reviewをbindすべきexact identity |
| subtitles | official JA JSON3 77 cue; Keifont 100px; max 2 lines; overflow/overlap/negative/orphan 0 | caption timingとpresentationを同じ動画で確認可能 |
| audio/signal | -14.61 LUFS; -1.58 dBTP; max adjacent delta 0.94 LU; black/silence event 0 | internal machine QA pass、production mix承認ではない |
| validation | 19 review-visible checks pass、page 200 / MP4 Range 206、desktop/mobile overflowなし | 技術欠陥をhuman editorial reviewから分離 |
| resume | 0.328s、renderなし、同一video/manifest SHA | 同じfingerprintのfail-closed再開を確認 |

この成果が開いたのは「編集構成、字幕presentation、画面、音声を一本でhuman reviewできる」状態まで。
rights、production subtitle/design/render、thumbnail、winner、public/publishing、uploadは開いていない。

## portable証拠とこのcheckoutのlocal artifact

| 対象 | このcheckout | 現在可能な動き |
|---|---|---|
| OUT-13 code/docs/tests | 存在、full suite pass | 実装修正、test、code review、contract監査 |
| OUT-13 source/transcript/caption/rights | 存在 | planが復元できれば別identityで再生成可能 |
| OUT-13 editorial plan input | 不在 | source-host回収または根拠付き再作成が必要 |
| OUT-13 final/review package | 不在 | port 8076やlauncherを利用可能とは報告しない |
| OUT-12 package | 存在 | predecessorをsame-machineで再検査可能 |
| OUT-12 final MP4 | live SHA `5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584` | tracked contractとexact一致 |
| protected R3 preview | 存在、cleanup除外 | pending/historical review evidenceを保持 |

OUT-13 packageを別hostから移す場合は、private transport方式、ACL、保持期限、削除/rollbackをownerが
明示する。Gitへmediaを追加する方法は採らない。exact packageを回収できず再生成する場合は、docsのrangesを
無言で同一planとみなさず、plan payload hashと新artifact identityを作り、旧SHAとの同一性を主張しない。

## 現在の判断packet

人間判断が必要なのはOUT-13 exact MP4一本に対するinternal editorial reviewである。確認軸は
編集構成、caption presentation、画面、音声。結果は`accept`、理由付き`bounded repair`、`reject`の
いずれかをexact SHAへbindする。

このcheckoutでは対象packageが不在なので、先に次のどちらかを満たす。

1. 生成hostまたは承認済みprivate transportから、manifest/hashを保ったexact packageへ到達する。
2. exact packageを回収できない場合、plan authorityを復元し、新artifact identityとして再生成・再検証する。

human review前にproduction/public gateを開かない。artifact accessの欠如をhuman rejectionや実装失敗とも
解釈しない。

## 受入監査

| 区分 | 判定 | 理由と次の扱い |
|---|---|---|
| OUT-13実装をrealと呼ぶ前のmust-fix | なし | explicit plan検証、render、subtitle presentation、machine QA、review生成、resume、testsがsource-host evidenceとtracked codeで成立し、このcheckoutでも全suiteがpass |
| human editorial acceptance前のmust-fix | exact package access | current rootにplan/packageがなく、一本を見ずにaccept/repair/rejectできない。M2で回収またはnew identity rebuild |
| 許容して延期するdebt | OUT-12 second-source repeatability、private transport、production各gate | OUT-13 codeの成立を壊さない。human review後に別sliceとして優先順位付け |
| docs debt | host-local availabilityをcanonical Runtimeから分離して読む必要 | Runtime/CURRENT_HANDOFFはsource-host artifact契約を保持し、本報告とproject-contextがこのcheckoutの不在を補足。`spec-index.json`欠如は既存stale referenceで今回のspec移動なし |
| next-slice seed | M2 artifact access、M4 bounded repair、M6a rights | 互いに目的が違うため一括実装せず、current consumerに最も近いM2/M3から進める |

この監査はOUT-13をproduction milestoneへ膨らませない。成立済みなのはreviewable internal slice、未成立なのは
このcheckoutからのexact review accessとhuman acceptance、その後のowner gateである。

## 可能な限り先まで見通した目標案

以下は依存関係を見失わないためのgoal ladderであり、着手承認そのものではない。各段階は目的、効果、
必要条件、最小証拠、ownerを分離する。

| 段階 | 目的と効果 | 着手条件 | 完了を示す最小証拠 | 状態 / owner / 次の動き |
|---|---|---|---|---|
| M0: sync + dev readiness | remote codeを安全に再開し、環境問題とproduct問題を分離 | current repo | branch parity、606 tests、GUI/CLI smoke、tracked episodes 0 | 完了 / Agent / 回帰時のみ再実行 |
| M1: OUT-13 implementation baseline | explicit plan→editorial MP4→reviewを一identityにする | OUT-12 operational baseline | remote code/tests、source-host 19 checks、resume receipt | code complete / Agent / contract維持 |
| M2: exact artifact access | humanが同じbytesを探索なしで見られるようにする | source-host accessまたはapproved transport/rebuild authority | package manifest、final SHA、single open command、host availability readback | blocked for review / Human owner + Agent / routeを一つ選ぶ |
| M3: internal editorial review | composition、subtitle、picture、audioのconsumer判断を閉じる | M2 exact artifact | exact SHA-bound accept/repair/reject receipt | pending / Human reviewer / 一本を通して判断 |
| M4: bounded closure | review欠陥だけを直し、修復loopを無制限化しない | M3がrepairならscope明示、acceptなら変更不要 | one bounded rerender、19 checks、再review receipt、lineage | conditional / Agent + Human / source-specificに閉じる |
| M5: main integration | current development laneをportable正本へ戻す | M3/M4 closure、clean merge preflight | main merge、full suite、dashboard/docs consistency、origin parity | not started / Agent / acceptanceをmergeと混同しない |
| M6a: rights clearance | 技術成功と利用許可を接続 | source/range、guideline snapshot、rights owner | allow/deny/restriction、時点、reviewerを持つreceipt | pending / Rights owner |
| M6b: production subtitle design | font/license、line break、safe area、speaker表現を制作判断へ上げる | M3 accepted、design owner、対象artifact | exact visual receipt、font license/readback、適用/非適用範囲 | closed / Human designer |
| M6c: production render acceptance | internal MP4をdelivery仕様へ上げる | delivery profile、device/color/audio QC、M6b合成条件 | full decode、device QA、exact SHA、human production receipt | closed / Supervisor/User |
| M7: episode candidate convergence | rights/subtitle/renderの独立結果を一画面へ束ねる | M6a〜M6cの各receipt | gateを混同しないepisode manifest、lineage、deferred理由 | proposed / Agent + Supervisor |
| M8: thumbnail + metadata | video確定後の手戻りを減らす | 3〜5本のaccepted output、thumbnail再開判断 | reproducible cover contract、exact thumbnail acceptance、metadata draft | parked/proposed / Human + Agent |
| M9: private/unlisted delivery | public化前にOAuth、idempotency、rollbackを証明 | M6〜M8、credentials明示承認 | dry-run、private/unlisted video ID、visibility/thumbnail receipt、retry/rollback | 未実装・要承認 / Human owner |
| M10: explicit public release | 公開判断を監査可能に閉じる | M9、全owner receipt、公開値とrollback | pre-public decision packet、visibility/made-for-kids明示、公開後receipt | future gate / Human owner |
| M11: multi-episode operations | 単発成功からqueue/retry/retention/quality trendを持つ運用へ移る | M1〜M10のcontract安定、複数episode evidence | failure isolation、observability、retention、複数episode回帰、operator cockpit | long-range proposal / Agent + Operator |

critical pathは`M2 -> M3 -> M4 -> M5 -> {M6a, M6b, M6c} -> M7 -> M8 -> M9 -> M10 -> M11`。
M6a〜M6cは並行準備できるが、一つのpassを他の承認に代用しない。OUT-12 second-source
repeatabilityは残存debtであり、OUT-13が別sourceを使った事実だけではpassにならない。M5後に
route generalityを優先する場合、3分以上distinct sourceのOUT-12 repeat runを独立sliceとして戻す。

## 次に推奨する四つの入口

| 入口 | いま減らす摩擦 | 選ぶと次に可能になること |
|---|---|---|
| **Review — M2/M3** | exact OUT-13をこのcheckoutで見られないこと | 最短でeditorial acceptanceまたは具体的repair scopeを得る |
| **Restore — M2** | plan/package portabilityがないこと | same bytes review、または正直なnew identity rebuildを成立させる |
| **Audit — M4準備** | failure/repair条件がsource-host evidenceに偏ること | media access待ちでもbounded repairのstop条件を先に固める |
| **Advance — M6a** | 技術artifactと利用許可が分離していること | OUT-13受理後にproduction候補へ進めるrangeを確定する |

第一推奨は`Review — M2/M3`。ただし現checkoutではpackage不在なので、実行上はまず`Restore — M2`を
満たす。対象mediaを回収できない場合は、hash-bound planを新identityで再生成する方が、旧artifactと
曖昧に混ぜるより監査可能性が高い。

## 監修AIが維持する境界

- integration正本`main`とactive OUT-13 branchを区別し、未mergeをmergedと報告しない。
- OUT-10/11 accepted bytes、OUT-12 automation acceptance、OUT-13 source-host machine evidenceを理由なく再審査しない。
- OUT-13 artifact不在をaccept/rejectへ読み替えず、human decisionを代筆しない。
- `episodes/`をtrackせず、local media、credentials、`.serena`、他worktreeを保護する。
- rights、production subtitle/design/render、thumbnail、public/publishing/uploadを一括で開かない。
- source textからspeaker、歌唱、歌詞、rightsを追加推定しない。
