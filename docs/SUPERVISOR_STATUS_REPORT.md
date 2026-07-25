# OUT-13 M6 exact-artifact deny canonical-main closure・監修報告

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
