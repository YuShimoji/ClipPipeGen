---
id: decision-log
title: Decision Log - ClipPipeGen
type: durable_decision_log
status: current
last_touched: 2026-07-24
---

# Decision Log - ClipPipeGen

## 2026-07-24 — OUT-13 candidate 005 のremote同期と別端末handoffを更新

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
