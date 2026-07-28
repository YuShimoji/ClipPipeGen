---
id: decision-log
title: Decision Log - ClipPipeGen
type: durable_decision_log
status: current
last_touched: 2026-07-28
---

# Decision Log - ClipPipeGen

## 2026-07-28 — persona-led S1のtracked実装をremote再開可能にする

検証済みimplementation
`c10e99d6444b8270e3173dfbe004b2dc1ea84976`を
`origin/codex/s1-persona-led-subaru-digest-v1`へnormal pushした。fetch後のremote
readbackは同一SHA、upstream parityは`0 0`。これによりtracked code/docs/testsと
exact artifact identityはbranchから再開できる。基底側4 commitsは既存remote branch
`origin/codex/s1-two-source-common-context-probe-v1`の
`bafe25afe0d2cad0cfaa0a2bda432b7ac0ef8471`まで既に存在し、新規公開した未公開実装は
今回の1 commitだけである。

`episodes/`内のsource media、MP4、review packageはignoredかつtracked 0件を維持し、
pushしていない。別端末はpackage availabilityを推定せず、同一マシンのhuman reviewは
exact MP4 SHA
`ca2cf751dfab68e56e4322208f7b6c677a8247fec10cf86813fd3cf80a24e76c`
へbindする。remote syncはhuman editorial acceptance、rights、production、public /
monetized use、publication、upload、releaseを開かない。PR / merge / tag / release /
deploy / upload / publicationは行っていない。

## 2026-07-28 — 旧common-context probeをrejectし、persona-led通常配信digestへ置換

exact bound HEAD
`bafe25afe0d2cad0cfaa0a2bda432b7ac0ef8471`の旧artifact
`clip-s1-two-source-common-context-probe-v1-001`に対するhuman verdictを
`reject / BLOCK_CURRENT / superseded / not bounded_repair`として記録する。
official-animation素材、無関係なsubjectsをabstract ordered-cut similarityで接続、
concept-before-viewing不在、viewerによるthesis再構成、食事・作業中には高すぎる認知負荷、
というsignatureを歴史証跡へ隔離した。packageは削除・上書きせず、
active/default/accepted exposureから外す。

replacementは新identity
`clip-s1-subaru-ohasuba-20260718-20260725-digest-v1-001`。
fixed pairは通常配信`youtube:ib3DwHDI71Q`（2026-07-18）と
`youtube:rltNvZ_FY8Q`（2026-07-25）だけで、人物、日付、ドラゴンボール初見の変化、
短時間で追えるbenefitを7秒のopeningで宣言する。7 cutsは日付順、source switch 1回。
全隣接点はsame-topic continuationまたはvisible date/topic changeで、
abstract frameだけに依存するtransitionは0。

authority`CPG-AUTH-20260728-IB3DWH-PRIVATE-ACQUISITION-01`は
`youtube:ib3DwHDI71Q`のanonymous acquisitionへだけ使用した。最初のcanonical
whole-source attemptはtimeoutになったが、adapter cleanup contract、空target、
receipt/ledger不在、関連process不在から完了効果0を確定してから同じtargetを再開し、
format 18で一件だけ完了した。mediaは259,391,841 bytes / 5374.049524s /
SHA`cf6a010a26c1a159b902bb5412f952086c365ce7e73d3775ee5a25aaaa11d353`。
Cookie、login、OAuth、credential、membership access、別source取得は0。
7/25 mediaは既存exact bytes
SHA`5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240`
と既存receipt/ledgerのread-only reuseで、network acquisitionは行わない。

final MP4は54,881,314 bytes / 187.920s /
SHA`ca2cf751dfab68e56e4322208f7b6c677a8247fec10cf86813fd3cf80a24e76c`。
12 payloadのclosed manifest、self-integrity
`659897fef35965ede7c514767021522a903e41c0e24701ce2f796809dafd020f`、
ffprobe、full non-audible decode、focused 27 tests、wide/narrow muted browser、
page 200 / Range 206をpassした。browser/listenerは停止済み。

観測結果はtechnical reviewabilityを示すだけで、decision effectは
`PERSONA_LED_ORDINARY_STREAM_S1_CANDIDATE_READY_FOR_HUMAN_REVIEW`への移行。
editorial acceptance、rights clearance/approval、production、public/monetized use、
publication、upload、releaseは開かない。source-specific processing snapshotは
`local_private_review_only`の処理範囲であり、rights clearanceではない。根拠:
`docs/output_layer/S1_PERSONA_LED_SUBARU_DIGEST.md` +
exact ignored local package + `docs/CURRENT_HANDOFF.md`。

## 2026-07-27 — S1 tracking parityを再確認し、parallel OUT-14 v3を統合しない

primary checkoutはbranch`codex/s1-two-source-common-context-probe-v1`、HEAD
`9656f58e55136c4d4a32f758d65484f9610c6feb`でtracked / untracked clean、進行中Git operation 0。
`git fetch --prune origin`後もupstreamは同一HEAD、parity`0 0`、`origin/main...HEAD`は`0 2`。
behind-only updateはなく、pull / merge / rebase / stash / restore / cleanを行わない。

remoteのparallel branch`origin/codex/out14-editorial-presentation-v3`は
`06975b0e5edab2faed585fd7f5e82d9c699ec235`で、S1とは`origin/main`後に2対3 commitで分岐する。
これは別artifact、別presentation、別exact human-review gateであり、S1へmergeせず、
active artifact、next action、acceptanceを相互継承しない。current authorityは
S1 S4 human common-context reviewを維持する。

same-machine S1 packageはmanifest closed set、final SHA`dc621bfe...f95be`、
focused 12 tests、GUI/Electron smoke、review page 200 / MP4 Range 206を再確認した。
full 689 testsはpackage構築時のpassを保持し、docs-only同期では反復しない。
rights、production、thumbnail、publishing、upload、public releaseは閉じたまま。

## 2026-07-26 — materially distinctなtwo-source successorをS4 review待ちとして正本化

remote最新`origin/main`
`edb782acd1e06aca46e0a5d10295ea52f30ad5c7`を完全に含むbranch
`codex/s1-two-source-common-context-probe-v1`に、implementation revision
`a3771bc59cd58b05c00a570e1074118ace3dc15a`が存在する。これはOUT-13 Candidate 005を
改名・修復・再公開候補化するものではなく、新identity
`clip-s1-two-source-common-context-probe-v1-001`へ取得済み実source二本、別question/thesis、
別range inventory、別MP4を割り当てるmaterially distinct successor probeである。

exact local packageは19 payload files、final MP4 93,331,608 bytes / 98.896s、
SHA`dc621bfe4be95b1fcc22204942e744d3a4a5dd56600bd8987b7cb6f5b55f95be`、
tree digest`a46fd90d9b61b2251029168bab8b44a86f95536eaf574a1e7b19fd5b6af8364a`。
6 cuts、各source 3 cuts、5 switches、60 caption cues、3 creator commentary eventsを持つ。
manifest closed set、16 media/evidence checks、focused 12 tests、full 689 tests、GUI/Electron
smokeはpassした。

machine passはcommon-contextの意味判断を代行しない。current stateを
`S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW`、next actionを
`obtain_s4_human_common_context_verdict_on_exact_probe`とする。S4は中心問いの理解可能性、
二sourceの相互深化、attribution/context、commentary/caption分離だけを
`accept / bounded repair / reject`で判断する。

rightsは`not_granted`、production/public/monetized/uploadはfalse。OUT-13 Candidate 005は
`M6_CLOSED_DENY_EXACT_ARTIFACT`のread-only archive evidenceを維持し、そのinternal
acceptanceやpublic denyをS1へ継承しない。根拠:
`docs/output_layer/S1_TWO_SOURCE_COMMON_CONTEXT_PROBE.md` +
exact local manifest/hash readback + `docs/CURRENT_HANDOFF.md`。

## 2026-07-25 — exact accepted OUT-13をmainへfast-forward統合し、M5 baselineを閉じる

supervising authority
`clip-out13-main-integration-authorization-20260725-01`は、exact accepted feature revision
`18641fe917b084259869263e8db05d78325aa2db`を`main`へ統合する一回の権限を与えた。
fetch後もorigin/mainは`5d6f69a64d510508a1f78ab3111a7780913a019c`、
featureはexact `18641fe`、topologyは`0/15`、merge-baseはorigin/mainだったため、
local mainをff-only同期してからaccepted revisionへfast-forwardした。
squash、merge commit、force、履歴改変、PRは使っていない。

統合直後のmain treeはaccepted feature treeと同一で、accepted revisionはmainの祖先。
その後、Runtime/Handoff/README/history/statusをM4 complete / M5 passedへ同期し、
configured full suite、focused OUT-13 / acceptance / semantic authority / dashboard、
dashboard再生成、compile/static、diff/privacy境界をfinal closure treeで確認した。
`main_integration_approved=true`はこのexact integrationに消費済みで、新しいmedia reviewや
Candidate 006を作らない。受領receipt内の`main_integration_approved=false`は
M2受領時点のscopeとして不変に保つ。

次の状態はM6 rights readiness。source/range、利用条件snapshot、判断owner、
allow/deny/restriction receiptの必要項目を整理できるが、rights approval、
production subtitle/design/render、thumbnail、publishing、upload、release、
deploymentは未承認・未開始のまま。根拠:
`docs/RUNTIME_STATE.md` + `docs/CURRENT_HANDOFF.md` +
`docs/SUPERVISOR_STATUS_REPORT.md`。

## 2026-07-25 — candidate 005のuser acceptanceを記録し、同一mediaの重複reviewを閉じる

ユーザーはsupervising threadで
`clip-out13-editorial-video-candidate-v1-005`、final MP4 SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`へ
`accept`を与えた。対象は従来手順による内部の全編editorial / visual reviewで、
構成、編集フロー、字幕提示、内部用途の画質・音質に限定する。
`docs/output_layer/out13_human_acceptance_receipt.json`へuser authority、日付、
review context、accepted dimensions、media/package/implementation identityの分離を記録した。

同じmedia SHA、同じreview context、同じaccepted dimensionsにはacceptanceを継承し、
`human_review_pending=false`とする。candidate 004 / 005はreview-relevant media bytesが同じため、
004へ別の全編reviewを要求しない。package revisionまたはimplementation revisionだけの変更も
reviewを再開しない。将来のbounded repairは変更・因果影響のあるdimensionとtimestampだけを
再確認し、影響しない判断を継承する。

M2はclosed、M3 main-integration preflightを開始する。rights、production
subtitle/design/render、production image quality、thumbnail、publishing、upload、
public release、main integrationは未承認である。accepted mediaの再視聴やcandidate 006生成は
現在のnext actionにしない。

## 2026-07-25 — remote 2 commitをff-only同期し、candidate 005のlocal review-readyをlive復元

開始時のactive branchは`673da5d`でtracked / untracked clean、ignored `episodes/`は保持されていた。
`git fetch --prune origin`でremote`3964326`が2 commit先行と判明し、
`git pull --ff-only origin codex/out-13-editorial-video-candidate-v1`で取り込んだ。
取り込み後はupstream parity`0 0`、`origin/main...HEAD = 0 12`、
`origin/main`はHEADの祖先である。履歴改変、merge、main統合は行っていない。

remote最新のRuntime/Handoffはcandidate 005をcurrent checkout不在としていたが、
current rootの`episodes/out13_editorial_video_candidate_20260723`にはplan、candidate 004 / 005、
MP4、validation、launcherが存在した。source`6f78657e...103a`、
transcript`4a7b4fd8...3495`、caption`3c15535f...9919`、
rights`4302c4a1...7bb8`、plan`27ef1aa9...dac2`はcontractと一致した。
candidate 005は25 files / 87,123,995 bytes、final SHA`a76babda...bbb5`、
tree digest`ed45fd4c...040`。exact resumeはrenderなし、5 cache hits、digest前後不変、
ephemeral serverはpage 200 / MP4 Range 206で、検証後停止した。

従ってcurrent gateはprivate recovery / new identity rebuildではなく、
exact candidate 005へのhuman editorial `accept / bounded repair / reject`とする。
machine validationは人間全編視聴を代行しない。repair時だけcandidate 006以降を割り当て、
004 / 005は不変のまま保持する。`episodes/`はtracked 0件を維持し、
別hostでは同じavailabilityを推定しない。rights、production、thumbnail、
publishing/upload/public、main integrationは独立gateのまま。

## 2026-07-24 — `602ab50` follow-up同期と開発開始条件を再検証

active branch / upstreamが`602ab50240bbc8cf8899314679a268942834412d`で一致する状態から
`git fetch --prune origin`と`git pull --ff-only`を実行し、追加remote差分なし、
parity`0 0`を確認した。`origin/main`はHEADの祖先で、`origin/main...HEAD = 0 11`。
`npm ci`は23 packagesを再構成してvulnerability 0、Node / Electron smoke、
OUT-13 CLI help、fresh Python full suite 654 testsはすべてpassした。
この報告・handoff更新を1 commitとしてpushした後はupstream parity`0 0`、
`origin/main...HEAD = 0 12`がresume時の期待値になる。

candidate 004 / 005 rootと005 planは引き続き不在、protected R3 previewは存在する。
source / transcript / caption / rights SHAのlive readbackも直下のcurrent host auditと一致した。
従ってproduct decisionは変更せず、private recoveryまたは006以降のnew identity rebuildを
reviewより先に置く。監修向けroadmapはM0〜M15へ拡張したが、追加目標はproposalであり、
FEATURE status、rights、production、publishing/public gateを自動承認しない。

## 2026-07-24 — `673da5d`同期後のcurrent host auditを正本化

active branchを`558f681`からremote tip`673da5d`へff-only更新し、同期直後のupstream parity
`0 0`、`origin/main...HEAD = 0 10`、tracked / untracked cleanを確認した。
`npm ci`、Node / Electron smoke、OUT-13 CLI helpはpass。Python full suiteでWindows junction
検出2件を再現し、reparse-point判定を追加してfinal 654 testsをpassした。

current host`DESKTOP-U9P4LKJ`にはcandidate 004 / 005 root、plan、MP4、validation、launcherがない。
local source`e2206cef...2d18`、transcript`ef928d4e...b42d6`、rights`e6ea9471...64c12`は
candidate 005契約と不一致で、provider JSON3`3c15535f...9919`だけ一致した。
従って直下の「Thank端末でlocal reviewable」という節はsource-host readbackとして保持するが、
current local availability判断としてsupersedeする。

次はexact candidate 005の承認済みprivate recovery + SHA照合、または現在input authorityから
candidate 006以降をnew identity rebuildする。review対象bytes成立前にhuman verdictを求めず、
004 / 005を上書きしない。rights、production、thumbnail、publishing/upload、public、
main integrationはこの同期・修復から自動で開かない。根拠: live Git parity + local
`Test-Path` / SHA audit + full suite / GUI / CLI validation +
`docs/SUPERVISOR_STATUS_REPORT.md`。

## 2026-07-24 — OUT-13 candidate 005 のremote同期と別端末handoffを更新

この節のcandidate 005 local availabilityは上のcurrent host auditでsuperseded。
source-host machine receiptとportable code contractとしてのみ参照する。

`git fetch --prune origin` と対象branchへの `git pull --ff-only` を実行し、
`codex/out-13-editorial-video-candidate-v1` の HEAD / upstream を
`3fdad157c09cc925a50750135e14fff5faa832f2`、parity `0 0`、worktree cleanとして確認した。
`git ls-files episodes` は0件のまま維持し、生成mediaをGitへ追加していない。

Thank端末のignored packageをlive照合した結果、candidate 005は25 files / 87,123,995 bytes、
final MP4 SHA `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`、
`validation_readback.status=passed`、review launcherありである。従って状態はartifact recovery待ちではなく、
machine/browser検証済み・human editorial review pendingとする。candidate 004はparallel targetとして保持し、
005のacceptanceやrepairで上書きしない。

別端末からGitだけで取得できるのはcode/docs/tests/contractまでで、`episodes/`のexact packageと入力はportableではない。
exact bytesを別端末で見せる場合は承認済みprivate transferと全SHA照合、新しい候補を作る場合はnew identityとして
別plan/input fingerprint/final SHAを記録する。rights、production、thumbnail、publishing、public、main integrationは
この同期やmachine passから自動的に開かない。

## 2026-07-23 — `558f681`同期後のlive auditでlocal review-ready記録を撤回

active branchを`2d8c4d6`からremote最新`558f681`へ`git pull --ff-only`で更新した。同期時の
tracking parityは`0 0`、`main` / `origin/main`は`5d6f69a`、active branchはmainより4 commit先。
`558f681`はOUT-13 local review readinessを記録していたが、同期後のcurrent rootとrepository配下
worktreeをlive探索した結果、`editorial_plan_input.json`、OUT-13 output directory、final MP4、
readback、launcherは存在しなかった。

さらにlocal source SHA `6f78657e...6103a`、transcript SHA `4a7b4fd8...3495`、rights SHA
`4302c4a1...bb8`はtracked OUT-13契約値と不一致で、official JA caption SHA
`3c15535f...d169919`だけが一致した。このため、source-host receiptのfinal SHA
`84ed7aa6...791d7e2`、0.281s resume、HTTP 200/206はhistorical evidenceとして保持する一方、
current checkoutで利用可能とは扱わない。

`npm ci`、Electron 42.0.0、final full suite 606 passed / 68.84s、Node/Electron smoke、OUT-13 CLI
helpはpassしており、code development readinessはgreen。current next actionは、original exact
package/input setのprivate recovery、またはSHA不一致を明示したnew plan / new artifact identityでの
rebuildを選び、reviewable bytesを復旧してからhuman editorial reviewへ進むこと。人間判断、rights、
production、thumbnail、publishing/uploadは代行・承認しない。

## 2026-07-23 — latest remoteをff-only同期し、OUT-13 exact local reviewをcurrent gateへ進める

この節のlocal availabilityは後続の`558f681`同期後live auditでsuperseded。source-host receiptと
portable code contractは保持するが、current checkoutの入口としては使用しない。

active branch `codex/out-13-editorial-video-candidate-v1`をfetch後に`c1566b3`から`2d8c4d6`へ
`git pull --ff-only`で更新した。同期時の追跡先parityは`0 0`、`main` / `origin/main`は`5d6f69a`、
sync baselineはmainより3 commit先だった。履歴改変、merge、mainへの統合は行っていない。

依存は`npm ci`で再構築し、Electron 42.0.0、24 packages audit脆弱性0、full suite 606 passed / 65.37s、
Node/Electron smoke、OUT-13 CLI helpを確認した。live toolchainはCPython 3.11.0、uv/uvx 0.10.0、
Pillow 12.3.0、FFmpeg/ffprobe 8.1.1、yt-dlp 2026.03.17である。

前日の別時点readbackと異なり、このcheckoutにはOUT-13 `editorial_plan_input.json`、25-fileのreview
package、`final_video.mp4`が存在する。final SHAはtracked contractの`84ed7aa6...791d7e2`と一致し、
`--resume`は0.281秒・`render_executed=false`・manifest SHA不変、localhost smokeはpage 200 / MP4
Range 206だった。従ってartifact recovery goalを完了へ移し、current next actionをexact SHAに対する
human editorial accept / bounded repair / rejectへ進める。これは人間受理、rights、production、thumbnail、
publishing/uploadを代行・承認しない。根拠: live Git parity + full suite/GUI/CLI validation + local
plan/package/hash/resume/HTTP readback + `docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md`。

## 2026-07-22 — OUT-13 remote branchをcurrent development laneとして再開し、artifact不在を分離

この節のartifact不在は当時のcheckout readbackであり、2026-07-23の同一workspace再計測でsuperseded。
tracked portability境界は維持するが、current local availabilityは上の2026-07-23決定を正本とする。

`main`は`8faaab2`から`5d6f69a`へff-onlyで更新し、同時にremoteで検出した
`codex/out-13-editorial-video-candidate-v1`をlocal tracking branchとして再開した。active branchは
検証対象implementation headは`c1566b3`で同期時upstream parity `0 0`、`main`より2 commit先だった。
本報告を含むhandoff commitがその後のremote tipになる。OUT-13は未mergeのreview branchであり、
この同期・検証はmain integrationやhuman acceptanceを新たに承認しない。

依存を`npm ci`で復元し、Electron 42.0.0 / audit脆弱性0、
`uvx --with Pillow pytest -q` 606 passed、Node/Electron smoke、OUT-13 CLI helpを確認した。tracked/untracked
stateは開始時clean、`git ls-files episodes`は0件。したがってtracked codeは開発可能である。

一方、このroot checkoutにはOUT-13 source/transcript/caption/rights入力は存在するが、
`editorial_plan_input.json`とsource-hostのexact packageは存在しない。localhost 8076や`--resume`を
現在利用可能とは扱わず、exact MP4 SHA `84ed7aa6...791d7e2`へのhuman editorial reviewは、生成hostへの
アクセス、承認済みprivate transport、またはhash-bound planを用いた新identity再生成の後に行う。
OUT-12 packageは存在し、final SHA `5d391ffd...a584`がtracked契約と一致した。根拠:
live Git parity + full suite/GUI/CLI validation + `docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md` +
root checkout artifact existence/hash readback。

## 2026-07-21 — OUT-12 remote handoffをmain正本へ固定

handoff更新直前の`main` / `origin/main`は
`f9cfc1194368087c49ffd98b69f880d6109cabfb`で一致し、upstream parityは`0 0`、
`git ls-files episodes`は0件だった。OUT-12の判断経緯、再開順序、証跡identity、未承認gateを
`RUNTIME_STATE`、`CURRENT_HANDOFF`、`project-context`、本log、`idea-ledger`、監修報告へ同期し、
別端末では`main`をfetch / ff-only pullしてこのtracked contextから再開する。

Gitで移送するのはcode/docs/testsとexact contractまでで、実source、最終MP4、QA画像、localhost
packageは引き続きignored `episodes/`内の同一マシン証拠である。本handoffは新しいacceptanceを
作らず、OUT-12 internal automation acceptanceを維持する。次は異なる3分以上の実sourceによる
repeatability、または明示承認されたrights / production subtitle design/render / thumbnail /
private transport gateのうち一つだけを開く。

## 2026-07-21 — OUT-12 one-command real video automationをinternal operationalとして受理

OUT-11 closure後の次sliceを、汎用framework拡張ではなく「取得済み実source一本から長尺MP4と
検証・review packageまでを一コマンドで生成できる」という観測可能な縦糸に限定した。
`youtube:gUwJBRUIWow`全長を11 cut / 260.693767sのH.264/AAC MP4へ生成し、exact SHA
`5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584`、13 validation checks、
mapping coverage 1.0、browser/HTTP QA、hash-verified resumeをpassしたため、状態を
`AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1`とする。

初回runで検出したAV stream duration差とtrue peak超過は、failure evidenceを保持したうえで
corrective passにより0.008767s / -1.44 dBTPへ修復した。mobile review表のdocument overflowと、
Windowsでbrowserがmedia Rangeを中断した際のserver traceも、生成CSSとconnection handlingで
修復した。これらはsource-specific manual patchではなく次runにも効くroute修復である。

この受理はinternal automationに限定する。rights pending、production subtitle/design/render、
thumbnail、winner、public/publishing、uploadはfalseのまま。caption authorityはtiming/containment
readbackであり、歌唱・歌詞・speaker・意味を自動主張しない。根拠:
`docs/output_layer/OUT_12_ONE_COMMAND_REAL_VIDEO_AUTOMATION.md` +
`clip-out12-one-command-real-video-automation-v1-001` + exact machine validation/resume readback。

## 2026-07-21 — OUT-10 / OUT-11 exact acceptance closure

添付実行契約に含まれる人間判断を、同一マシンの実媒体から再取得した完全SHA、bytes、durationへ
bindした。OUT-10 `62d4b45b...97cdd`は発話直後の軽い切断感をsource-specific debtとして許容し、
延長による次scene侵入を避けるため再修復しない。SOURCE-05 `b4a01413...a4969`はsource EOFまで
切断感なしのBGM・映像中心PV候補として受理するが、歌唱・歌詞・話者は未確認のままにする。

closure順はOUT-10、OUT-11。5 sourceはaccepted internal、winnerなし。Short追加生成・endpoint修復・
再レビューを閉じ、OUT-12 one-command real video automationへ進む。rights、production、thumbnail、
public/publishingは別gate。根拠: `docs/output_layer/out11_human_acceptance_receipt.json` + live media hash/probe +
`docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md`。

## 2026-07-21 — OUT-11修復レビュー待ちをremote再開境界として固定

検証済み実装head `249b3308b0d8a1cc8b75d37a245d717322859133`では、初回人間レビューを
旧candidate identityへbindし、SOURCE-04を同じSHA `465d732c...16524`の
`accepted_internal` receiptへ移した。OUT-10は`0.000–34.785s`、SHA
`62d4b45b...97cdd`へ、SOURCE-05は`202.586–260.643s`、SHA
`b4a01413...a4969`へ修復済みだが、二本の新bytesはまだ人間未受理である。

このhandoffでは、OUT-09を指していた`project-context`、`decision-log`、`idea-ledger`と、
HUB-01を先頭に出していた長期`HANDOFF.md`の入口をOUT-11へ同期する。これはdocsの再開契約を
current runtimeへ合わせる変更で、candidate acceptance、winner、rights、production、thumbnail、
public/publishing、main mergeを新たに承認しない。

remote branchは`codex/out-11-five-source-short-portfolio-wave-v0`。tracked code/docs/testsとexact
identityはGitで別端末へ渡すが、ignored `episodes/`内のMP4・QA・localhost packageは同一マシン
限定証拠のまま。別端末で映像レビューが必要な場合は、承認済みtransport方針または既存契約に
沿う再生成を別途行い、Gitへmediaを追加しない。根拠: `docs/RUNTIME_STATE.md` current capsule +
`docs/CURRENT_HANDOFF.md` + `docs/output_layer/OUT_11_FIVE_SOURCE_SHORT_PORTFOLIO_WAVE.md` + live Git parity。

## 2026-07-19 — OUT-09 exact candidateをaccepted_internalとしてcanonical mainへ閉じる

Web Supervisor経由のユーザー自由記述を、MP4 SHA
`b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`へbindした。
字幕と音声の一致、短い字幕の切替と可読性、初期自動再生・突然の音がないこと、foreground
server accessの維持、発話途中ではない終端はいずれもpassし、overallをinternal review用途で
acceptする。`human_review_pending=false`、`acceptance_granted=true`、
`candidate_01_acceptance=accepted_internal`とする。

上下のblur/mosaic状canvasは、source `640x360`の下部74px native caption bandを除外し、
`0,0,640,286`だけで余白を補完して元焼き込み字幕とshort cueの二重表示を防ぐ
source-specific処理として今回だけacceptableだった。記録値は
`source_specific_caption_band_suppression_observed_acceptable_not_generalized`。美観、共通Shorts
design、caption bandのないsource、重要内容とcropが衝突するsource、production subtitle
design/image qualityへは昇格しない。

merge-preflightではorigin/main `29a1a519`とsource branch `17436ad`を同一toolchain/font環境で
比較し、既知OUT-06 reviewed-wrap 2件が双方で同一失敗となることを確認した。optional policy
未指定のdefault render commandもSHA `a863ee1a...7ebf`で一致したため、branch-only regressionは
false。OUT-06 debtはparkし、OUT-09または次製品レーンへ便乗修正しない。

次候補は`OUT10_THIRD_SOURCE_SHORT_PORTFOLIO_EXPANSION`一件だけをdata-onlyで保持する。本決定は
OUT-10実装、rights、production、thumbnail、public/publishing、portabilityの承認を含まない。
根拠: user acceptance + `docs/RUNTIME_STATE.md` current capsule + exact package hash readback +
origin/main対source branch regression comparison。

## 2026-07-17 — sync auditはOUT-08 closureを維持し、OUT-09をproposalのままにする

`main`を`origin/main`の`b3cec5d`までfast-forwardし、parity `0 0`、tracked
worktree cleanを確認した。同一マシンのOUT-08二本はaccepted SHA-256と一致し、
R3 operator surfaceも`review_ready=true`だった。一方、bare `uvx pytest -q`は
Pillow未注入でcollection停止するため、full validation contractは
`uvx --with pillow pytest -q`とし、521 tests passを確認した。

この監査は新しいproduct acceptanceを開かない。OUT-08はclosed、rights/
production/thumbnail/public/publishingはclosedまたはpending、OUT-09は
`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY` proposal-onlyのままとする。修復前の
review待ち説明と`sub_102`例外を残していた`docs/index.md`はcurrent closureへ合わせる。
長期目標は監修提案としてidea ledger/reportへ置き、feature statusや実装承認へは
自動昇格させない。根拠: `docs/RUNTIME_STATE.md` current capsule + live Git/package/
test readback。

## 2026-07-17 — OUT-08 exact二本をaccepted_internalとして閉じる

Web Supervisorが、`cut_009`を完全除外した修復後exact candidate 01 / 02への
ユーザー回答「両方問題ありません」を受領済みであることを正本へ統合した。

- batch: `accepted_all_internal`
- candidate 01 / 02: `accepted_internal`
- accepted IDs: both
- winner: none
- `human_review_pending=false`
- `acceptance_granted=true`

対象identityはcandidate 01 SHA
`f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a`、candidate 02 SHA
`47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b`。
candidate 02 max source end `135.219`はreject interval `135.219–144.000`と非交差で、
`cut_009=reject`を維持する。`sub_067` / `sub_068`はこのexact render内だけで受入済み。

正本lineageはsource tip `2d45bd8d9ff5cb5f2efcdeeaa839b4ef000e96a2`。
recovery tip `d1f44d17e9747419f307706cad802aefdd012efd`は
`PARKED_OPTIONAL_NONCANONICAL_INFRA_PROOF`としてremote保持し、mainへ統合しない。
package欠落、server停止、private transfer未実行はclosure blockerではない。

rights、production render、production subtitle design、thumbnail、public/publishing、
upload/OAuth/visibility/made-for-kidsは閉じたまま。次のdata-only successorは
`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY`で、このdecisionは実装承認を含まない。

## 2026-07-15 — OUT-08 の cut_009 source-time exception を廃止

supervisor correction により、`cut_009` が final decision `reject` のままであることと、
その素材を candidate へ使わないことを別契約として固定した。candidate 02 は
`81.298–98.315`、`98.315–116.467`、`116.934–135.219` の三範囲だけを使い、
旧 `137.054–138.055` / `sub_102` dependent payoff 例外は plan、validator、tests、
readback、HTML、current docs から除去した。

validator は authority ID、label、dependent flag より先に source-time overlap を
検査し、`cut_009` reject interval `135.219–144.000` と交差する range を render
前に拒否する。candidate 01 は再renderせず SHA-256 を保持し、candidate 02 の実装
baseline は remote commit `9ab8445afa247d07b46ef031cdc30f3fbbafafdd`。

状態は `OUT08_CUT009_FULLY_EXCLUDED_CONTRACT_REPAIRED_REVIEW_READY` で human
review pending、既存 acceptance boundary は不変。review package は tracked 0 の
same-machine evidence で、別ホストへ自動 transport されない。根拠:
`docs/RUNTIME_STATE.md` current capsule +
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md`

## 2026-07-15 — OUT-08 active / OUT-07 parked の regression 境界を固定

full suite で、OUT-07 時代の test が `artifacts/ACTIVE_REBUILD.json` を current
active contract として要求し続けていることが判明した。現行正本では OUT-08 の
same-machine package が active review evidence であり、同 JSON は OUT-07 の parked
predecessor contract である。test はこの二つを同時に検証する形へ更新する。

この変更は artifact、caption/cut authority、human decision、rights、production、
public/publishing gate を変更しない。根拠: `docs/RUNTIME_STATE.md` current capsule +
`docs/output_layer/OUT_08_REAL_UNUSED_RANGE_SHORT_MINIBATCH.md`

## 2026-07-14 — OUT-08 を review-ready で停止

OUT-08 は、既使用範囲を避けた real source authority から 2 本の vertical Shorts
internal review candidate を atomic package として生成する slice として完了した。
人間レビューに必要な映像・字幕・音声・境界・manifest readback は揃っているため、
次のボトルネックは実装ではなく candidate ごとの編集単位レビューである。

維持する状態:

- `human_review_pending=true`
- `authority_mutated=false`
- `cut009_final_cut_decision=reject`
- `production_candidate=false`
- `production_acceptance=false`
- `production_subtitle_design_acceptance=false`
- `rights_approval=pending`
- `public_or_publishing_acceptance=false`

この停止は、未観測の direct seek を自動で合格扱いせず、字幕の残存 review debt を
production typography の品質保証へ拡大しないためのものでもある。

## 2026-07-14 — OUT-07 を predecessor として固定

OUT-07 の main commit `4fad107ca5ecb9c86de2df73f08dedfbe14cf9c9` は
`PARK_PROVISIONAL_USABLE`。この episode に対する canonical pattern、default
template、selected thumbnail とはみなさない。OUT-08 の active readback と
`artifacts/ACTIVE_REBUILD.json` の parked OUT-07 rebuild contract を混同しない。

## 2026-07-14 — remote 同期境界を確定

実装・docs・判断ログは branch
`codex/out-08-real-unused-range-short-minibatch-v0` の
`d3798c4cf1c622631b9a1089634909475d640b9f` にあり、upstream との距離は `0 0`。
`episodes/` は意図的に ignored のまま、tracked episodes は 0 件である。したがって
別端末で Git clone から再開できるのはコードと判断文脈までで、レビュー動画 package
は同一端末のローカル証拠として別途再生成または承認済み artifact transport が必要。

## 未解決の設計判断

人間が candidate 01 / 02 を一本の編集単位として評価し、必要ならテンポ・境界・字幕・
音声の違和感を自由記述する。その返答なしに candidate を selected、production、public、
publishing-ready へ遷移させない。
