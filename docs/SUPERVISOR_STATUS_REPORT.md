# M2 closure / M3 verdict — READY_FOR_EXPLICIT_MAIN_INTEGRATION

更新日: 2026-07-25 JST

対象: ClipPipeGenのみ

active branch: `codex/out-13-editorial-video-candidate-v1`

accepted artifact: `clip-out13-editorial-video-candidate-v1-005`

## 監修時に最初に押さえる結論

M2はclosedである。ユーザーはexact final MP4 SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`を、
従来手順による内部の全編editorial / visual reviewとして`accept`した。
受領範囲は構成、編集フロー、字幕提示、内部用途の画質・音質であり、
`docs/output_layer/out13_human_acceptance_receipt.json`へuser authority、日付、
review context、accepted dimensionsとidentity分離を記録した。

M3 main-integration preflightの実判定は
`READY_FOR_EXPLICIT_MAIN_INTEGRATION`。feature branch全差分、tracked/ignored境界、
sensitive data、現在状態とOUT-13回帰、Python static、diff hygieneを監査し、
main統合を止めるcurrent blockerは見つからなかった。

この判定はmain統合の承認ではない。`main_integration_approved=false`を維持し、
明示承認まではmainへのmerge/pushを行わない。rights、production
subtitle/design/render、production image quality、thumbnail、publishing、upload、
public releaseも未承認である。

## M2受領receipt

| 項目 | 記録値 | 意味 |
|---|---|---|
| artifact | `clip-out13-editorial-video-candidate-v1-005` | accepted package revision |
| media SHA | `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5` | 人間判断をbindするmedia identity |
| media | 82,594,810 bytes / 128.833333s / 1920x1080 / H.264 High + AAC | exact review target |
| verdict | `accept` | user authorityによるinternal editorial acceptance |
| recorded at | `2026-07-25T02:58:58+09:00` | receipt記録時刻 |
| context | `out13_candidate_005_internal_full_view_editorial_visual_review_v1` | 従来手順の内部全編review |
| accepted dimensions | editorial composition / flow、subtitle presentation、内部用途のpicture / audio quality | 受領が成立した判断範囲 |
| package revision | 25 files / 87,123,995 bytes / tree digest `ed45fd4c...040` | mediaとは別のpackage identity |
| implementation revision | candidate contract `3fdad157...32f2`、受領記録base `d753ea7...acb1` | media/packageとは別のcode identity |
| receipt | `docs/output_layer/out13_human_acceptance_receipt.json` | trackedでportableな正本 |

package内の古い`visual_observation=unverified`は、生成時のmachine-only package fieldとして
履歴を保つ。人間受領は別receiptに記録し、packageを上書きしない。

## 同じ媒体を再審査へ戻さない規則

acceptance identityは次の三要素で決める。

1. media SHA
2. review context ID
3. requested dimensionsがaccepted dimensionsに含まれること

この三要素が同じなら`human_review_pending=false`を継承する。package revisionまたは
implementation revisionだけが変わっても人間reviewを再開しない。candidate 004と005は
final MP4がbyte-identicalで同じSHAのため、同じcontextとdimensionsについて004を別途
全編視聴する必要はない。

将来のbounded repairでは、実際に変えた、または因果的に影響するdimensionだけを再開する。
timestampで限定できる変更は該当intervalだけを再確認し、影響しないdimensionとintervalは
今回の受領を継承する。media SHAが変わる場合は新しいreview identityを起票する。

この契約は`tests/test_out13_human_acceptance_receipt.py`で次を回帰化した。

- same media / context / dimensionsではreview gateを生成しない
- package / implementation revisionだけの変更ではreviewを再開しない
- bounded subtitle repairはsubtitle dimensionと指定timestampだけを開く
- rights / production / public / main integrationは閉じたまま
- current stateにself-referential commit placeholderを残さない

## Git topologyとremote同期

M3開始時点の確認値:

| 対象 | 値 | 判定 |
|---|---|---|
| branch | `codex/out-13-editorial-video-candidate-v1` | 想定branchと一致 |
| feature remote tip | `d753ea7bb4b48bb98da1fc16afc073d20432acb1` | fetch後にlocal/upstream一致 |
| `origin/main` | `5d6f69a64d510508a1f78ab3111a7780913a019c` | feature branchの祖先 |
| upstream parity | `0 0` | M3開始時に同期済み |
| `origin/main...HEAD` | `0 13` | main側取りこぼし0、OUT-13側13 commit |
| remote | `https://github.com/YuShimoji/ClipPipeGen.git` | fetch/push同一remote |
| effective Git identity | `YuShimoji <shimoji0902@gmail.com>` | 直前commit identityと整合 |
| tracked `episodes/` | 0 files | private/generated media境界を維持 |

現在のacceptance/preflight変更は一つの論理commitとしてfeature branchだけへpushする。
tracked文書内に最終commitの自己参照を置かず、実際のtipはGit自体を正本にする。

## mainに対する全差分

preflight対象は`origin/main`から現在treeまでの22 files。

| 境界 | ファイル数 | 主な内容 | 判定 |
|---|---:|---|---|
| product code | 3 | OUT-13 CLI、main command registration、editorial renderer | review branchで実装済み |
| tests | 4 | OUT-13 renderer、current state/dashboard、acceptance dedup | targeted green |
| docs / contracts | 13 | Runtime/Handoff、OUT-13 contract、receipt、decision/idea/project context、artifact registry | current stateをM2 accepted / M3へ統一 |
| generated docs | 2 | `docs/dashboard/index.html`、`project-status.json` | existing generatorで再生成する既存surface |
| private/generated media | 0 | `episodes/`、MP4、caption package、framesなど | tracked差分なし |

product codeはM2 closure mission中に変更していない。受領記録、current-state docs、
既存テスト期待値、新しいdedup regressionだけを追加した。

branch historyとworktree差分を対象に、以下を確認した。

- `episodes/`配下のtracked fileなし
- MP4、audio、image、archive、database、cacheなどのmedia/generated binary追加なし
- Windows/macOS user-profileの絶対path追加なし
- private key、API key、GitHub token、access/refresh token、client secret、password assignment追加なし
- candidate 003 / 004 / 005 package、plan、caption、manifest、MP4への書込みなし

## package保全claimの範囲

OUT-13の保全claimは、リポジトリが実装するlocal threat modelに限定した。

- 通常ファイルと正規化path
- local pipelineのgeneration / resume / failure-reconciliation経路
- symlink / junction拒否
- manifest/file hashとpackage-tree digestによるexact-byte/content consistency

権限を持つ外部process、OS/filesystem侵害、監査外の同時改変まで防ぐ一般セキュリティ保証は
主張しない。これらの外部攻撃仮説はnonblocking debtであり、今回のM2受領またはM3判定を
開き直す理由にしない。historical artifact IDやstate文字列は識別子として保持するが、
current説明から「永久」「絶対trust」と読めるclaimを除いた。

## 検証結果

| 検証 | 結果 | 判定に使えること |
|---|---|---|
| remote fetch / branch / upstream / main ancestry | pass | 同期済みfeature branchを監査 |
| accepted MP4 SHA / bytes | exact match | user verdictとmedia identityの一致 |
| candidate 004 / 005 MP4 equality | same SHA | duplicate full-view gate不要 |
| tracked `episodes/` | 0 | private media非追跡 |
| focused OUT-13 + current state + dashboard | 93 passed in 13.19s（final rerun） | renderer既存contractと新receipt/current stateが整合 |
| acceptance/current-state subset | 35 passed in 0.91s（post-dashboard final rerun） | dedupとdashboard routeを最終確認 |
| `python -m compileall -q src tests` | pass | Python syntax/import compilation |
| new acceptance test Ruff | pass | 今回追加testのformat/static |
| `git diff --check origin/main` | pass | whitespace errorなし |
| sensitive/media diff scan | no matches | tracked境界に新しい漏えいなし |
| previous full suite at unchanged product implementation | 654 passed in 94.36s at `d753ea7` | product codeの既存全体回帰 |

このmissionではproduct codeを変更していないため、full suiteは再実行していない。
直前tip`d753ea7`の654 passedをimplementation evidenceとして保持し、今回変更した
docs/tests/current-stateに比例した93-test gateを実行した。

参考として、projectにRuff設定やlint scriptがない状態でlatest Ruffをbranch全Python差分へ
探索的に当てると、今回追加test以外の既存branch code/testsに15件のimport-order、
typing import、broad exception、冗長cast、explicit `check`指定の指摘が出る。
これは定義済みCI gateではなく、compile/full/targeted testsはgreenであるため
current integration blockerにはしない。将来lint policyを導入する場合は別のbounded cleanupにする。

## M3 decision packet

結論: `READY_FOR_EXPLICIT_MAIN_INTEGRATION`

理由:

- origin/mainの最新祖先を含み、main側の未取込commitがない
- OUT-13のproduct implementationは直前full suite green
- acceptance/dedup/current-state変更はtargeted 93 tests green
- tracked media、credentials、machine-specific absolute pathの追加がない
- ignored/private artifact境界とtracked `episodes/` 0件を維持
- current docsはM2 accepted / M3 preflightへ統一され、同一media再reviewを要求しない
- rights/production/public/main approvalを内部受領から推定していない

current blocker: なし。

明示判断が必要なもの: main integration authorizationのみ。承認されるまではmainを変更しない。

## 未承認gate

以下はM3 readyでも開かない。

| gate | 現在状態 | 開くために必要なもの |
|---|---|---|
| main integration | unapproved | explicit authorization |
| rights / material use | pending | source/range別の権利owner判断とreceipt |
| production subtitle design | false | exact visual design review、font/license、safe-area policy |
| production render | false | delivery codec/color/audio/device QC profileと受領 |
| production image quality | false | delivery contextでのvisual QC |
| thumbnail | false / parked | accepted video群と比較方針、human selection |
| publishing metadata | not approved | title/description/attribution/visibility decision |
| credentials / OAuth | not authorized | user-managed credential gate |
| upload / private delivery | not attempted | idempotency、rollback、visibility確認 |
| public release | not approved | rights + production + publishing ownerの最終明示判断 |

## 可能な限り先までの目標設定

長期目標は依存順で進め、各段階のexit evidenceが成立してから次を開く。

| 段階 | 目標 | exit evidence | 現在状態 / 次のowner |
|---|---|---|---|
| M0 Remote convergence | feature branchをremote最新へff-only同期 | parity 0/0、main ancestry、clean tracked | 完了 |
| M1 Exact artifact convergence | plan/input/package/mediaを一identityへ照合 | SHA、bytes、digest、HTTP/readback | 完了 |
| M2 Internal editorial acceptance | exact mediaを内部全編reviewで判断 | user receipt、scope、dimensions | 完了 |
| M3 Main-integration preflight | branch全差分と境界を監査 | 本報告のREADY verdict | 完了。明示判断待ち |
| M4 Explicit main integration | feature branchをmainへ統合 | authorization、merge SHA、remote main parity | User/Supervisor承認後 |
| M5 Integrated baseline verification | main clone相当で再現性を確認 | full suite、CLI/GUI smoke、tracked boundary | Agent |
| M6 Rights decision | source/rangeごとの利用条件を閉じる | allow/deny/restriction receipt、owner/date | Rights owner |
| M7 Production subtitle design | internal字幕をproduction designへ上げる | exact frames、font/license、safe area、human verdict | Designer/User |
| M8 Production render profile | delivery用映像音声仕様を確定 | codec/color/audio/device QC、exact output SHA | Production owner |
| M9 Episode acceptance pack | M6〜M8の独立receiptを一episodeへ束ねる | lineage-complete acceptance manifest | Supervisor |
| M10 Thumbnail and metadata | video確定後に外装を作る | comparison candidates、selected thumbnail、metadata draft | Human selection |
| M11 Private publish dry-run | 外部stateを変えずpublish contractを検証 | dry-run receipt、idempotency key、rollback plan | Agent + credential owner |
| M12 Private/unlisted delivery | 限定公開でend-to-endを確認 | upload receipt、visibility readback、rollback proof | User |
| M13 Explicit public release | 公開判断を監査可能に閉じる | rights/production/publishing owner receipts | User final gate |
| M14 Multi-episode operations | queue/retry/retentionを複数episodeで証明 | failure isolation、SLO、quality trend | Operations owner |
| M15 Policy-constrained autonomy | 繰返し作業を安全に委譲する | allowlist、budget、stop conditions、audit log | Supervisor/User |

M4〜M15は提案であり、FEATURE statusや各gateの承認を自動変更しない。最短critical pathは
`explicit main authorization -> M4 integration -> M5 baseline verification`。その後は
rights、subtitle design、render profileを別々に閉じる。

## 次の取っ掛かり

- **Advance**: M3 packetを確認し、main統合を明示承認する。承認後にM4/M5が可能になる。
- **Audit**: M6 rights packetをsource/range単位で作る。制作成功と利用許可の混同を解消する。
- **Explore**: M7 production subtitle designをthin slice化する。内部字幕からdelivery visualへ進める。
- **Verify**: main統合後のclean-clone/full-suite/GUI/CLI gateを先に設計し、M5の完了条件を固定する。

現時点で個別candidateへの過剰調整、docsだけの停滞、統合先不明のartifact追加は発生していない。
current next consumerはmain integrationの明示判断を行うUser/Supervisorである。
