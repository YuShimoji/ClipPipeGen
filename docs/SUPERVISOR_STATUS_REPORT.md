# OUT-14 Push Micro-Arc real stream・監修引継ぎ報告

更新日: 2026-07-26 JST

対象: ClipPipeGen のみ

## 監修時に最初に押さえる結論

`clip-out14-push-microarc-stream-v1-001`は
`OUT14_PUSH_MICROARC_REAL_STREAM_READY_FOR_HUMAN_REVIEW`。実在する完了済み公開配信
`youtube:rltNvZ_FY8Q`から、一週間の不在理由、帰省・葬儀の背景、地元と家族の具体話、
「帰れて良かった」という結びまでを、一つの連続した701.166667秒のmicro-arcにした。

機械的には source/acquisition/caption authority、Timeline IR、字幕mapping、H.264/AAC
1920x1080、full decode、audio/signal、manifest閉集合、resume、localhost page/Rangeが
green。final MP4 SHAは
`1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f`。
人間によるeditorial / visual / language acceptanceは未実施である。

## Git と保存境界

| 対象 | 観測・実施 | 現在状態 |
|---|---|---|
| remote baseline | `git fetch --prune origin`後、`origin/main` exact `edb782acd1e06aca46e0a5d10295ea52f30ad5c7`を確認 | OUT-14開始点として固定 |
| isolated development | `codex/out14-push-microarc-real-stream-v1`をexact mainから別worktreeへ作成 | tracked変更はこのbranchだけ |
| active worktree | 元の`codex/s1-two-source-common-context-probe-v1` worktreeは開始時clean、HEAD/upstream `9656f58e...` | read-only境界。変更しない |
| remote mutation | push / PR / merge / main integration | 未実施・未承認 |
| media storage | source、receipt、plan、MP4、review packageは`episodes/`配下 | ignored、`git ls-files episodes` 0を維持 |
| preserved evidence | Candidate 005、M2、M6、S1 rejected two-source probe | 内容とidentityを変更しない |

このbranchは最終的に一つのlocal commitへ閉じる。commitしてもupstreamへpushせず、
remote `origin/main`は変わらない。private mediaとgenerated packageはGit cloneでは
別hostへ移動しない。

## portfolio reset と今回実装した範囲

出力delivery contractをsource countから分離し、次の三つを正本へ置いた。
これはcodec・解像度・縦横比のvideo profileではない。

| profile | 解く視聴体験 | このスライス |
|---|---|---|
| `PUSH_MICROARC` | 一つの出来事を発端から余韻まで短編として届ける。通常5–15分 | 実装し、実artifactを生成 |
| `EVENT_STACK_RECAP` | 一つのevent期間のbeatとstate changeを積み上げる。通常9–30分 | 登録のみ。未実装 |
| `CATALOG_TOPIC_FEATURE` | 複数の独立話題を章立てで整理・比較する。通常15–45分 | 登録のみ。未実装 |

OUT-14 runの属性は`push / free_talk / solo / single_talent / ja`。delivery lane、
collaboration、talent scope、language、content classを別軸にしたため、将来のprofile routerが
「N-sourceだからcatalog」のような誤った分類をしない。

active quarantineは`two_source_forced_alternation_common_context_v1`、
`unrelated_context_official_anime_interleave_v1`、
`shorts_attention_reset_as_longform_default_v1`。rejected two-source probeを
開始候補・修復対象・美容調整対象にしていない。

## source と取得

選定sourceは大空スバルの
`【#生スバル】おはすば！：FREE TALK【ホロライブ/大空スバル】`。
provider infoは`was_live=true`、`live_status=was_live`、`availability=public`、
release `2026-07-25T01:02:27Z`。concert、song、members-only、第三者game IPを避けた。

既存yt-dlp 2026.03.17のnative transportは0-byte partのまま停止したため、boundedに停止し、
project-local ignored tool directoryへyt-dlp 2026.07.04 + curl-cffiを置いた。
`fetch-source-video`へ任意の`--impersonate-target`と`--yt-dlp-downloader`を追加し、
`Chrome-133:Macos-15` / `ffmpeg` / progressive format 18で85.934秒の取得に成功した。
global toolやcredentialは変更していない。

| receipt | SHA / 値 |
|---|---|
| source MP4 | `5e026c94...d240`; 244,453,290 bytes; 4848.047891s; 640x360 H.264/AAC |
| video acquisition receipt | `7c8e32e6...9426` |
| normalized PCM audio receipt | `b3fdc3ae...e905`; WAV `449e22aa...1c83` |
| material ledger | `ba864bde...dcac` |
| provider info | `3d99dc0e...d32` |
| provider auto caption | `011d8a82...739`; `ja-orig` JSON3 |
| anonymous caption receipt | `59101758...9d3`; cookies/OAuth false |
| rights snapshot | `7336b78b...8d7`; compliance pending |

provider自動字幕は選定とtimingの証拠。公式著者字幕、逐語 transcript、話者同定、
permissionの根拠にはしていない。

## episode plan と成果物

source 786.36–1487.52秒を一続きで使い、前後を2つのintentional omissionとして完全に
source complementへした。semantic roleは意味の確認点で、映像上の汎用章ラベルや
不要なjump cutではない。

| role | source range | 編集上の役割 |
|---|---:|---|
| hook / inciting situation | 786.36–826.92 | 一週間の不在から帰省を明かす |
| necessary context | 826.92–958.32 | 祖母の逝去と葬儀という背景 |
| development / escalation | 958.32–1200.00 | 田舎の人・動物・環境の具体話 |
| payoff / resolution | 1200.00–1410.12 | 家族とのやり取りとハロハロの出来事 |
| completing aftermath | 1410.12–1487.52 | 後日談から「帰れて良かった」へ着地 |

source冒頭で本人がpremiseを説明するためcreator contextは0件。省略理由と
source-caption / creator-context別namespaceをreadbackした。

finalはH.264 High / AAC / yuv420p / 1920x1080 / 30fps、701.166667秒、
157,691,184 bytes。取得source 640x360をLanczosで拡大し、native 1080pとは主張しない。
metadata draftはsource URLを1行目、exact source titleを2行目に置き、非公式編集・
非endorsementを明記した。

## 検証結果

| 観点 | 結果 | 意味 |
|---|---|---|
| focused regressions | acquisition 21 passed、OUT-13/14近接回帰 86 passed、single-cut修正後 81 passed | 新profileと既存profileの最小回帰 |
| media | full decode exit 0、faststart、53,901 packets / regressions 0、A/V start delta 0 | 再生・timestamp整合 |
| audio/signal | -15.0 LUFS、-1.19 dBTP、black 0、silence 0 | 技術異常なし |
| captions | 178 cues、overlap/negative/orphan 0、mapping coverage 1.0 | timing/container整合。言語正確性は含まない |
| manifest | 29 payload rows、payload tree `ac8c6253...4d03`、self-integrity `f0da343f...b403` | package閉集合 |
| complete package | 30 files / 162,017,845 bytes、tree `7fae710b...b8fa` | exact local review identity |
| resume | 2.822秒、renderなし、同一SHA | 再入可能 |
| localhost | page 200、MP4 Range 206 / 1024 bytes | video-first browser delivery |

成功runの内訳はsource/plan 0.808秒、caption 0.036秒、render 231.839秒、
validation 165.352秒、review package 101.475秒、pre-manifest 499.617秒。
最初のrunは単一cutにinternal boundaryがないため既存helperのsampleが空になり、
`contact sheet has no samples`でfail-closedした。単一cutでは選定区間endpointsを証拠化する
限定修正後に成功し、失敗stagingを成功packageへ昇格させていない。

## 代表フレームの技術観察

first/middle/last、source selected range、通常・2行・短時間字幕frameを実際に開いた。
sample範囲では字幕の画面外clipping、source字幕との二重表示、破損frameは見つからなかった。
2行字幕は大きく下部に置かれるが画面内に収まる。

ただし、自動字幕の短時間sampleには`ない方がいいって言われて、猿 / み`のような
不自然な語分割があり、0.834秒で読むには負荷が高い。この点はmachine validationの失敗ではなく、
human language/editorial reviewの具体的な確認項目である。

## 人間の判断パケット

exact SHA `1db41c4f...d07f`を全編開き、次を判断する。

1. 786.36秒の開始が自然で、1487.52秒の余韻までで一話が閉じるか。
2. 葬儀を含む個人的内容をこのpremiseで扱う編集判断が適切か。
3. 178 provider-auto cuesを公開品質へ近づける言語校正がどこまで必要か。

選択肢は`accept / bounded_repair / reject`。acceptは内部editorial/visual/language scopeだけ。
bounded repairはaffected timestamp/caption/layoutだけを新identityにする。rejectはこのexact
artifactの内部候補役を閉じる。どの選択もrights、production、YPP、thumbnail、Shorts、
upload、publication、visibilityを開かない。

## 今後の条件付き目標

| 目標 | 可能になること | 開始条件 | gate |
|---|---|---|---|
| O14-H1 exact human receipt | PUSH profileの人間評価を再利用可能にする | 現package全編レビュー | exact SHA/context/dimensionsにbind |
| O14-H2 bounded repair | 字幕・boundaryの実欠陥だけを直す | H1=`bounded_repair` | affected dimensions再review |
| O14-P1 profile rubric | delivery intentで比較できる | PUSH receipt | 未実装profileを生成済みと書かない |
| O15 Event-stack specimen | event recapの因果・state changeを検証 | event boundary一次証拠 | aftermathまでの人間評価 |
| O16 Catalog specimen | 章立て型の異なるbottleneckを検証 | 適格な複数話題source | chapter relationの人間評価 |
| O17 delivery-contract router | source countとdelivery intentを分離して自動選択 | 三contractのspecimen | fail-closed routing tests |
| O18 reproducibility/security | 別hostで再構成可能にする | 採用profile方向 | fresh clone own install、dependency/security audit |
| O19 rights/production decision | exact release candidateの可否を判断 | owner/territory/platform/素材権利確定 | 独立approval receipts |
| O20 authorized release loop | 公開と測定を安全に行う | O19明示承認とcredentials | upload/publication/rollback receipts |

H1がrejectならH2を飛ばし、理由をprofile rubricへ戻す。rights/public gateが閉じたままでも、
O15–O18のlocal internal specimenとreproducibilityは進められる。

## 次に推奨する取っ掛かり

| 入口 | 解く摩擦 | 次に可能になること |
|---|---|---|
| **Advance** | exact MP4の判断待ち | acceptならportfolio比較、bounded repairなら限定修正へ進む |
| **Audit** | 自動字幕の言語不確実性 | cue単位の修正量と公開品質までの距離が分かる |
| **Explore** | PUSHだけでは比較不能 | CatalogまたはEvent-stackの最小source候補をread-only選定できる |
| **Verify** | ignored artifactの別host非可搬性 | fresh-clone再現要件とprivate artifact store要件を定義できる |

## 実行していないこと

`EVENT_STACK_RECAP`生成、`CATALOG_TOPIC_FEATURE`生成、generic N-source profile、
generated image、thumbnail、Shorts derivative、push、PR、merge、main integration、
upload、publication、visibility changeは行っていない。真の停止条件は発生していない。
現在残るのは人間の編集・言語判断と、明示承認が必要なrights/production/public gateである。

# Historical — OUT-13 M6 exact-artifact deny canonical-main closure

更新日: 2026-07-26 JST

対象: ClipPipeGen のみ

## 監修時に最初に押さえる結論

OUT-13 M6 は `M6_CLOSED_DENY_EXACT_ARTIFACT` でclosedした。ユーザーは監修役の
推奨1「deny — exact MP4の収益公開は行わず、後継版へ移る」を選択し、project publication
decision ownerとして、次のexact identityだけにdenyを与えた。

| 判断軸 | bindした値 |
|---|---|
| packet | `clip-out13-m6-rights-decision-readiness-v1-001` |
| starting packet revision | `dac5f7fb715cb3a7acd6c982a80cb916492e7880` |
| artifact | `clip-out13-editorial-video-candidate-v1-005` |
| exact MP4 SHA-256 | `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5` |
| public use | `deny` |
| monetized YouTube use | `deny` |
| rights approval | `not_granted` |
| durable evidence | `docs/rights/out13_m6_rights_decision_readiness_packet.json#/decision_history/0` |

Candidate 005は削除、変更、rejectしていない。M2で受領された内部editorial evidenceと
technical provenanceを保つread-only archive evidenceへ役割を固定し、public defaultをoff、
production / publishing / upload / release候補集合から除外した。M2の
`human_review_pending=false`とaccepted dimensionsは維持する。

deny-binding revision
`097fcaad8985d4f24077da484819efb5942b9c65`は、authority
`clip-m6-deny-main-integration-20260726-01`により通常fast-forwardでcanonical `main`へ
統合され、remoteへpush済みである。live tipはtracked文書へ未来のcommit SHAを自己参照
させず、`refs/heads/main`で解決する。現在の再開branchは`main`、remote decision
bindingはavailable、main/upstream parityは`0 0`である。

## 判断の意味と境界

今回のdenyは、Candidate 005のexact MP4をpublicかつ収益化検討対象として使う経路を閉じる
project-controlled decisionである。ユーザーを元動画、caption、font、音楽、人物、埋込み要素の
rightsholderとは表明しない。infringementその他の法的結論、素材一般のallow/deny、
将来artifactへのdenyも含まない。

このため、次の二つを同時に正本へ残した。

- exact Candidate 005のpublic / monetized pathはclosedであり、現在のproductionやreleaseへ
  戻してはならない。
- source permission、全7区間のcontent observation、provider captionの再製根拠、exact Keifont
  bytesのlicense/NOTICE bindingは未解決であり、rights approvalへ昇格させてはならない。

未解決証拠は、deny済み経路を閉じる目的に限ってnonblockingである。Candidate 005を公開へ戻す
ための免除ではなく、将来successorへ自動継承できる権利判断でもない。

## 変更していないidentityと既存受領

| 対象 | 現在の扱い | 変更有無 |
|---|---|---|
| Candidate 005 media bytes | exact SHAのinternal evidence | 変更なし |
| M2 acceptance receipt | composition、flow、subtitle presentation、内部用途のpicture/audio quality | 変更なし |
| `human_review_pending` | `false` | 維持 |
| M4 main integration | `complete` | 維持 |
| M5 integrated baseline verification | `passed` | 維持 |
| Candidate 003–005 private package | `episodes/`配下のsame-machine ignored evidence | 変更・削除なし |
| rights material/range rows | permission/content observation不足を保持 | individual verdictは`undecided`のまま |

overall project publication verdictは`deny`だが、8 material rowsと7 range rowsの
`owner_verdict=undecided`は意図的に維持した。これは「素材ごとのrightsholder判断が済んだ」
という誤読を防ぐためである。

## 正本とconsumerの状態

| consumer | 現在状態 | 次に使う情報 |
|---|---|---|
| Runtime / Handoff | `main`上の`m6_closed_deny_exact_artifact` | successor scope決定まではCandidate 005をinternal evidenceとして保持 |
| M6 packet | deny eventとexact evidence locatorを保持 | 判断日、ユーザー指示、開始revision、artifact ID、SHA |
| dashboard | Runtimeからclosed stateを投影 | public default off、次action |
| M2 acceptance consumer | accepted internal dimensionsを継承 | 同一SHA/contextへの再reviewを作らない |
| future successor lane | 未開始 | 新identityとmaterially distinct scopeを先に決める |

現在のsingle next actionは
`require_materially_distinct_successor_artifact_before_any_new_public_or_monetized_consideration`。
successorの作成、設計、spec、renderは今回のMissionに含めていない。

## Git・portability・外部状態

historical preparation branchは`codex/m6-rights-decision-readiness-v1`、packet準備revisionは
`dac5f7fb715cb3a7acd6c982a80cb916492e7880`、deny-binding revisionは
`097fcaad8985d4f24077da484819efb5942b9c65`である。`5bd6e653... -> dac5f7fb... ->
097fcaad...`を通常fast-forwardとして`main`へ統合し、remoteからpacketをreadbackできる。
old feature branchはhistorical evidenceであり、current resumption targetではない。

packetと正本文書はGit portableだが、Candidate media/packageは`episodes/`配下のignored
same-machine evidenceでありportableではない。`git ls-files episodes`は0件を維持する。
mainへのpushは完了したが、PR、tag、release、deployment、upload、publish、visibility変更、
credential/OAuth操作は行っていない。

deny-binding作成時に実行されたconfigured full Python suiteは、post-integration
resume reconciliationのclosure evidenceには使わない。これはprior nonblocking process
deviationとしてのみ保持し、今回の判断根拠はfocused regressions、generated dashboard
readback、JSON、diff、remote refに限定する。

## 受入条件

closed stateを正しいと扱うためのmust-pass条件は次の通り。

1. decision eventが開始packet revision、packet ID、Candidate ID、exact MP4 SHA、日付、
   user evidence locatorへ結び付く。
2. public useとmonetized YouTube useだけがdenyで、rights approvalは`not_granted`。
3. Candidate 005はinternal evidenceとして保持され、production / publish / upload /
   release候補から除外される。
4. M2 acceptanceと`human_review_pending=false`が変わらない。
5. individual material/rangeの未解決状態がallow/clearedへ変換されない。
6. 将来artifact、underlying sources、font、captions、embedded elementsへdenyを一般化しない。
7. Runtime、Handoff、OUT-13 live capsule、dashboard、focused testsが同じcanonical stateと
   single next actionを示す。
8. media、receipt、application code、remote stateを変更しない。

## 今後の条件付き目標

denyにより従来の `M6 -> M7 production subtitle -> M8 render` という直線は閉じた。
今後はsuccessorを起票するかどうかの判断から再開する。

| 段階 | 目標 | 開始条件 | exit evidence |
|---|---|---|---|
| S0 Successor scope decision | public / monetized considerationを再開する価値と方針を決める | ユーザーの明示判断 | materially distinct scope、禁止継承、owner |
| S1 New identity allocation | Candidate 005と混同しない新artifactを割り当てる | S0承認 | new artifact ID、input boundary |
| S2 Transformation/content strategy | 何をどう変えて公開適合を目指すか決める | S1 | source/material/range strategy、excluded paths |
| S3 Fresh rights inventory | successorで実際に使う素材だけを再棚卸し | S2 | material/range/terms/unknowns packet |
| S4 Internal editorial review | exact successor mediaの構成・視聴品質を判断 | render可能な実体 | exact SHAにbindしたreceipt |
| S5 Rights/publication decision | successorのexact intended useを人間が判断 | S3/S4 | allow/deny/restrict evidence。rightsと公開を分離 |
| S6 Production design/render | 許された素材と条件でdelivery仕様を確定 | S5 allow範囲 | subtitle/font/license、codec/audio/device QC |
| S7 Episode acceptance pack | lineageと判断receiptを一つに束ねる | S6 | no-scope-widening manifest |
| S8 Thumbnail/metadata | rights-cleared素材でhuman choiceを作る | S7 | selected candidate、source credit、restrictions |
| S9 External-state dry-run | upload前契約を変化なしで確認 | S8 | idempotency、rollback、visibility plan |
| S10 Private/unlisted delivery | 明示authority下で限定導通 | credential/visibility承認 | upload receipt、readback、rollback |
| S11 Public release decision | public化を個別判断 | 全receiptと最終owner approval | explicit release decision |
| S12 Operations | 複数episodeの再現性と監査を確立 | 成功例と失敗例 | isolation、SLO、retention、rights trend |

S0が承認されるまではS1以降を開始しない。Candidate 005をsuccessorのように改名したり、
同じSHAへ別のpublic reviewを付けたりして閉鎖判断を迂回しない。

## 次に推奨する取っ掛かり

- **Advance**: successor scope decisionだけを行う。公開経路を再開する価値、変える素材、
  transformationの差分を決めると、新identity allocationを安全に起票できる。
- **Audit**: packet、Runtime、Handoff、dashboardのdeny projectionをread-onlyで監査する。
  closed stateのdriftやCandidate 005のcandidate-set再混入を早期に検出できる。
- **Excise**: 将来のproduction/publish selectorがCandidate 005を参照する場合の拒否条件を、
  successor Missionで実装候補として切り出す。今回はapplication codeを変更しない。
- **Explore**: rights riskを下げるmaterial strategyを複数案だけ比較する。実素材取得、
  license research、spec、renderはS0承認後に限定する。

現在のdrift監査では、docsだけを増やして実装に戻れない状態ではなく、deny decisionのconsumer
投影とnegative testが今回の成果物である。一方、successorの具体化は未承認なので意図的に
先送りしている。
