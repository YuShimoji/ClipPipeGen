# ClipPipeGen 同期・開発再開・長期目標提案 — 2026-07-17

## 監修上の結論

ClipPipeGen は `main` を最新の `origin/main` へ fast-forward し、OUT-08 accepted
internal closure を基準に開発再開できる状態へ戻した。追跡済みworktreeはclean、
upstream parityは`0 0`。このworkspaceに残るignored OUT-08 packageは、tracked docsが
受理対象として固定したexact二本とSHA-256が一致する。

OUT-08に追加実装や追加人間レビューは不要。次のproduct bottleneckは、同じ一つの
sourceで成功したShorts pipelineが別source/episodeでも成立するか未証明なことにある。
したがって次の推奨目標は、未承認proposal
`OUT09_SECOND_SOURCE_SHORT_REPEATABILITY`をnarrow sliceとして承認し、別sourceまたは
episodeから最低1本の12〜60秒・9:16・reviewable candidateを、大規模rewriteなしで
生成すること。これは提案であり、この報告だけでは実装承認に昇格しない。

## 同期と作業環境

| 確認対象 | 実測結果 | 開発への意味 |
|---|---|---|
| remote fetch | `git fetch --prune origin`成功 | `origin/main`とremote branchを2026-07-17現在へ更新 |
| 開始branch | `codex/out-08-real-unused-range-short-minibatch-v0`、upstream `0 0` | feature tip自体は同期済みだった |
| mainとの差 | feature tipは`origin/main`の直系1コミット手前 | merge/rebase判断なしにfast-forward可能だった |
| 現在branch / HEAD | `main` / `b3cec5d45425fe4ea1bcb447a93c15a4c071410d` | canonical OUT-08 closure上で再開する |
| upstream parity | `HEAD...origin/main = 0 0` | remoteへ未取得・未送信のtracked commitなし |
| tracked worktree | clean | user変更を混ぜずに次sliceへ入れる |
| untracked cleanup | 空の`docs/verification/`のみpath-scopedで除去 | 不明な内容やepisode evidenceは削除していない |
| ignored state | `episodes/`、`node_modules/`、cache類あり | runtime evidenceと実行依存が同一マシンにある |
| cleanup protection | R3 `human_preview_session/`あり | broad `git clean -fdX`は禁止のまま |
| tracked episode paths | 0件 | source media / render / subtitle payloadをGitへ混入していない |

## 現在のスライスと受理済み成果

OUT-08は、既使用`cut_001..cut_003`とreject済み`cut_009`を避け、未使用実素材から
二本のvertical Shorts候補を作った。修復後exact二本へのユーザー回答
「両方問題ありません」はtracked authorityへ結び付け済みである。

| 対象 | 構成 | 実尺 / 字幕 | SHA-256 | 現在状態 |
|---|---|---:|---|---|
| candidate 01 | `cut_004 50.868–60.277` + `cut_005 60.277–79.163` | `28.266667s` / 17 | `f7ea3f7097118656ebfd36f13cd698c11f0fcf04f042e8fe507965af073e388a` | `accepted_internal` |
| candidate 02 | `cut_006 tail 81.298–98.315` + `cut_007 98.315–116.467` + `cut_008 116.934–135.219` | `53.466667s` / 54 | `47c844b1e74aac10d37c8cfc470ba84eb9915a5707dd84028be5b227344d593b` | `accepted_internal` |
| batch | 二本を一括したatomic package | target 2 / actual 2 | manifest self-integrity `22c7137d81361f662a3053fbd796837f16a58473ba0ecbcb99bb0e031499b4a4` | `accepted_all_internal`、winnerなし |

candidate 02の最大source endは`135.219`で、`cut_009` reject interval
`135.219–144.000`とoverlapしない。修復前の`137.054–138.055` / `sub_102`例外は
現行plan・validator・packageから除去済みで、復活させない。

## live readbackとtracked authorityの分離

同一マシンのpackageは次に存在する。

```text
episodes/jp_pilot01_hololive_bancho_20260525/review/out08_real_unused_range_short_minibatch/
```

- `candidate_01.mp4` / `candidate_02.mp4`の実ファイルhashは上表と一致した。
- `batch_readback.json`は生成時点の
  `OUT08_REAL_UNUSED_RANGE_SHORT_MINIBATCH_REVIEW_READY`を保持する。
- 後から受領した人間判断は`docs/RUNTIME_STATE.md`、`docs/CURRENT_HANDOFF.md`、
  `docs/decision-log.md`、`artifacts/ARTIFACTS.md`へexact identity付きで記録済み。
- packageを再生成・書換えしてacceptanceを埋め戻す必要はない。package欠落やserver停止も
  記録済みacceptanceを失効させない。
- `status-episode`はR3 operator surfaceについて`review_ready=true`、missing artifact 0、
  rights `pending`、`production_candidate=false`を返した。これは過去/下位層の証拠が
  読めることを示すだけで、OUT-08を人間レビュー待ちへ戻さない。

必要な時だけ、repository rootから次を実行してexact二本を再表示できる。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\jp_pilot01_hololive_bancho_20260525\review\out08_real_unused_range_short_minibatch\open_preview.ps1 -Port 8071
```

navigation JPGは候補識別用frameであり、thumbnail candidateやthumbnail acceptanceでは
ない。

## pipeline全体の現在地

| workflow段階 | 可能になっていること | 残る主要gap |
|---|---|---|
| source / material | local/URL source audio/video取得adapter、ledger、receipt、source identity | 次sourceの選定・取得承認とcross-source再現性 |
| transcript | Vosk JP/EN、公式subtitle track import、review patch、schema readback | 公式字幕なしsourceの品質比較、話者分離、GUI correction |
| editing | cut生成、context check、subtitle draft、chapter/review packet、NLE CSV | creative/production cut acceptance、FCPXML/Resolve XML |
| diagnostic output | tiny proofからOUT-03〜OUT-08のreal vertical internal candidateまで | multi-source repeatability、production render acceptance |
| subtitle presentation | Keifont系diagnostic evidence、line-break/readback、exact OUT-08 acceptance | production subtitle design acceptance、source横断rule |
| thumbnail | YMM4 slot patch、OUT-07 provisional usable direction | 3〜5本portfolioでの比較、canonical/default判断 |
| rights | manifest/readback、pendingでもlocal diagnostic継続 | human rights/material-use clearance |
| publishing | metadata/upload/thumbnail/OAuthをintegration候補として分離 | 実装、credentials、safe visibility、receipt、rollback |
| operator surface | CLI、docs dashboard、read-only/action GUI、artifact-specific launcher | episode全体を一画面で再開する統合cockpit |

## 完了度の見立て

- 現スライス OUT-08: `██████████ 100%` — 実装、repair、exact human acceptance、main
  closureまで完了。
- multi-source internal-review workflow: `██████░░░░ 60%` — sourceからreviewable
  vertical outputまで通るが、成功例が実質一つのsource familyへ偏る。
- production/public delivery north star: `████░░░░░░ 40%` — 接着層は広く存在するが、
  production render、rights、thumbnail、publishingの独立gateが閉じている。

後二つはacceptance値ではなく、次の投資順を決めるための計画上の概算である。

## 開発を先へ進める目標階段

| 段階 | 達成目標 | 完了信号 | 先に必要なもの | 現在状態 / owner |
|---|---|---|---|---|
| G1 | OUT-09 second-source repeatability | 別source/episodeから12〜60秒・9:16・reviewable candidateを最低1本、大規模rewriteなしで生成 | explicit slice approval、source方針、rights readback | proposal-only。Supervisor/Userが承認、Agentが実装 |
| G2 | 3〜5本のreal Shorts portfolio | source別の境界・字幕wrap・音量・再生性scorecardとfailure taxonomy | G1成功と追加episode evidence | 未起票proposal。Agentがcontract案、Supervisorが一般化範囲を判断 |
| G3 | production limitation lift | production renderとproduction subtitle designを別々にaccept/rejectできるexact packet | G2再現性、明示的production slice | gate closed。Human decision ownerが対象を限定 |
| G4 | rights/material-use clearance | 一候補について利用条件・制限・判断者・receiptが明示される | source identityとrights owner | `rights=pending`。Human rights ownerの判断が必要 |
| G5 | thumbnail system再開 | 3〜5本を比較し、偶然でないcover方向を選べる。canonical/defaultは別判断 | G2 portfolio、複数方向、独立review | OUT-07 parked。Supervisor/Userが再開可否を決める |
| G6 | private/unlisted delivery | dry-run、safe visibility、upload/thumbnail receipt、rollback付きhandoff | G3〜G5の必要gate、OAuth/credential承認 | PB/YouTube integration未実装。外部状態変更前にhuman approval |
| G7 | episode operator cockpit | intake→evidence→decision→deliveryを一画面で追跡し、artifact探索を減らす | 安定したG1〜G6 contract、episode_pack、private artifact方針 | 既存GUI/CLIは点在。consumer-first vertical sliceが必要 |
| G8 | multi-episode production-assist loop | 複数source/episodeでtraceable artifact、判断receipt、rollback、公開handoffを再現 | G7、retention/privacy、運用KPI | 長期north star。公開判断そのものは自動化しない |

最終deliverable像は、承認済みsourceを入力し、source/rights/transcript/edit/subtitle/
output/thumbnail/publish metadataを一つのepisode lineageでつなぎ、各人間gateを越えた
ものだけをprivate/unlisted/public deliveryへ渡し、全操作をreceiptとrollback情報で
再現できるproduction-assist loopである。

## 監修役に求める次の判断

推奨はG1を次のactive sliceとして承認すること。承認時に最低限、次を固定する。

1. source方針: 既存localの別episodeを使うか、新しいlow-risk public sourceを別途承認する。
2. acceptance: 12〜60秒、9:16、最低1本、direct review可能、authority/receipt/hashあり、
   `production_candidate=false`、rights statusをreadbackする。
3. non-goals: production/public acceptance、thumbnail再開、publishing/OAuth、artifact
   portability一般化、pipeline大規模rewriteを含めない。
4. stop condition: candidateを作れない理由をfailure taxonomyとして記録できた場合は、
   無理にrender成功へ寄せずG1の有効なdiagnostic outcomeとして監修へ返す。

承認がまだ出ない場合も開発はblockedではない。次の独立入口がある。

- **Audit**: `sub_067` / `sub_068`のexact acceptanceを全動画共通ruleへ誤一般化しない
  cross-source scorecard準備。
- **Excise**: 1,900行超のRuntime historical sectionと
  `FEATURE_REGISTRY.md`のmojibakeを別docs-health sliceで整理し、one-pass re-entryを改善。
- **Explore**: private artifact portabilityをepisode共通contractにするか評価。ただしstorage、
  retention、privacy、rollback承認が必要で、OUT-08 closure条件には戻さない。

## 検証結果と既知の開発上の注意

| command | 結果 |
|---|---|
| `uvx python -m src.cli.main status-episode --episode-dir episodes\jp_pilot01_hololive_bancho_20260525 --format json` | success。R3 `review_ready=true`、rights pending、production false |
| `uvx pytest -q` | collection error。`PIL`未注入で画像系2 moduleがimport不能 |
| `uvx --with pillow pytest -q` | final post-edit run: `521 passed in 126.92s` |
| `npm run smoke` | `gui smoke: OK` |
| `npm run smoke:electron` | `electron smoke: OK` |
| candidate MP4 SHA-256 readback | 二本ともaccepted identityと一致 |
| `git ls-files episodes` | 0件 |
| `git rev-list --left-right --count HEAD...origin/main` | sync直後`0 0` |

Pillowはreview/test用optional依存として既存docsに現れるが、full suiteには必須になって
いる。次terminalではbare commandではなく`uvx --with pillow pytest -q`を使う。将来、
dependency manifestを整備するなら別のsmall tooling sliceとして行い、Pillowをproduction
renderer dependencyへ誤昇格させない。

## 変えなかった境界

- rights approval: `pending`
- production render acceptance: `false`
- production subtitle design acceptance: `false`
- thumbnail acceptance: `false`
- public/publishing acceptance: `false`
- upload/OAuth/visibility/made-for-kids: unopened / not attempted
- `episodes/`: ignored、tracked 0
- optional recovery branch `d1f44d1`: parked noncanonical、mainへ未統合
- OUT-07: `PARK_PROVISIONAL_USABLE`、3〜5本揃うまで追加iteration禁止

この報告は次の開発目標を遠くまで並べるが、個々のproposalをapprovedへ遷移させる
authorityではない。次に実装してよいのは、監修役またはユーザーが明示的に開いた一つの
narrow sliceだけである。
