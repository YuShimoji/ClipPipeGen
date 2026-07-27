# ED-12 / S1 two-source common-context probe・監修報告

更新日: 2026-07-27 JST

対象: ClipPipeGen のみ

## 監修時に最初に押さえる結論

remote最新`origin/main`は`edb782acd1e06aca46e0a5d10295ea52f30ad5c7`でlocal mainと一致。
current branch`codex/s1-two-source-common-context-probe-v1`はそのmainを完全に含み、
同期監査開始時のHEAD / upstreamは
`9656f58e55136c4d4a32f758d65484f9610c6feb`でparity`0 0`。mainより2 commit先で、
implementation revisionは`a3771bc59cd58b05c00a570e1074118ace3dc15a`。本報告commit後の
remote exact HEADは`refs/remotes/origin/codex/s1-two-source-common-context-probe-v1`
をfetchして読戻す。

このcommitは、OUT-13 Candidate 005を変更・改名せず、新artifact
`clip-s1-two-source-common-context-probe-v1-001`を実装した。取得済み実source二本をexact
hashとdirect caption evidenceへbindし、creator-authored thesis/commentaryを別provenance
trackとして一つの98.896秒timelineへ組み立てる。code/packageの技術検証はgreen。
現在のsingle bottleneckはS4 human common-context reviewである。

| 監修軸 | current readback |
|---|---|
| branch | `codex/s1-two-source-common-context-probe-v1` |
| sync input HEAD / upstream | `9656f58e...c6feb` / parity `0 0` |
| base remote main | `edb782acd1e06aca46e0a5d10295ea52f30ad5c7` |
| implementation | `a3771bc59cd58b05c00a570e1074118ace3dc15a` |
| artifact | `clip-s1-two-source-common-context-probe-v1-001` |
| exact MP4 SHA-256 | `dc621bfe4be95b1fcc22204942e744d3a4a5dd56600bd8987b7cb6f5b55f95be` |
| package tree digest | `a46fd90d9b61b2251029168bab8b44a86f95536eaf574a1e7b19fd5b6af8364a` |
| state | `S1_S3_COMMON_CONTEXT_PROBE_READY_FOR_S4_HUMAN_REVIEW` |
| review | `human_review_pending=true` |
| rights/public | `not_granted` / `false` |

進捗は、current successor sliceのengineeringで
`[█████████░] 90%`（実装・実artifact・machine gate完了、S4未完）、
production/public delivery全体で
`[███░░░░░░░] 30%`（rights/design/render/delivery/releaseは未開始）と見積もる。
これはテスト件数を製品完成度へ置き換えた数字ではなく、残るgateのownerとexit evidenceに基づく。

## remote同期と開発可能性

2026-07-27のprimary checkoutはtracked/untracked cleanで、進行中Git operationは0。
protected R3 preview、OUT-13 package、S1 package、`.claude/worktrees/`、`.serena/`、
cache/node_modules/`_tmp`をignored stateとして分類した。`git fetch --prune origin`後、
current branchはupstream parity`0 0`、`origin/main...HEAD = 0 2`。behind-onlyではないため
pullは不要で、mainへのswitch、stash、restore、clean、rebase、mergeは行っていない。

remoteにはparallel
`origin/codex/out14-editorial-presentation-v3@06975b0e5edab2faed585fd7f5e82d9c699ec235`
も存在する。S1とは`origin/main`後に2対3 commitで分岐し、別artifactと別human-review gateを
持つため、今回統合しない。S1のcurrent authorityをv3へ上書きせず、どちらのhuman acceptanceも
他方へ継承しない。

依存とgate:

| 検証 | 結果 | 解釈 |
|---|---|---|
| `npm ci` | 23 packages、audit 0 vulnerabilities | GUI依存を再構築 |
| GUI smoke | pass | Node側読込経路が動作 |
| Electron smoke | pass、Electron 42.0.0 | desktop entryが起動可能 |
| S1 focused | 2026-07-27再実行、12 passed | identity、chronology、mapping、provenance、immutabilityを確認 |
| full Python suite | package構築時689 passed / 95.01s、今回未反復 | current implementationの既存回帰証跡を保持 |
| CLI help | pass | subcommand dispatchが利用可能 |
| package manifest | 2026-07-27再検証pass | 19 payload＋manifest、self-integrity一致 |
| review server | 2026-07-27 page 200 / MP4 Range 206 | browser向け入口とbyte-range配信を確認後、server停止 |
| Git/privacy | `git diff --check` pass、tracked `episodes/` 0 | private mediaをGitへ追加していない |

したがって、tracked codeの開発再開と同一マシンS4 reviewの双方が可能。別端末では
Gitだけでignored source media/review packageが移らないため、code development-readyと
artifact review-readyを分けて報告する。

## 実装された縦糸

source pairは次の二本。

| source | identity | direct evidence上の役割 |
|---|---|---|
| SOURCE-04 | `youtube:PQ54uUV41-k` | 困りごとに対し医者・魔法使い・科学者を試し、頼れる人不在へ進む |
| 秘密の診察室 | `youtube:TlnviOwLRmk` | 軽い症状が役割遊び、急患、オペ、過剰処置へエスカレートする |

中心問いは「助けを求める状況は、なぜ自信満々だが適合しない解決策の連鎖で悪化するのか？」。
working thesisはcreator-authored synthesisと明記され、source captionの発話事実と混同しない。

timelineは6 cuts、各source 3 cuts、5 switches、98.896秒。source内時系列、continuous output
clock、one cut / one source/input/range mappingを維持する。60 caption cuesは下部、
3 commentary eventsは上部compact band、source labelは左上。hard cut以外のtransition、
PiP、split screen、BGM、SFX、generated imageryは使わない。

machine validationはstream/codec/resolution/duration/timestamp/A-V delta/faststart/full decode/
loudness/source-switch loudness/black-silence/source mapping/both-source decode/caption containment/
commentary containment/provenance separationの16項目をpass。integrated loudnessは-14.85 LUFS、
true peakは-1.31 dBTP、最大隣接cut差は3.38 LU、black/silence eventは0。

代表contact sheetとcommentary contact sheetを監査時に開き、sample上の明白な欠落、
frame外caption/commentary、source label欠損は見つからなかった。これはsample observationであり、
全編の意味的S4 acceptanceではない。packageの`visual_observation.status=unverified`は変更していない。

## S4で必要な人間判断

技術greenが答えられない四問をexact SHAへbindする。

1. 中心問いが前知識なしでも理解可能か。
2. 二sourceが単なる交互配置を越えて、互いの意味を変化・深化させるか。
3. attribution/contextが正直で、sourceの意味を過剰に一般化していないか。
4. commentaryが関係を明確にし、source captionとの区別が知覚できるか。

回答は`accept / bounded repair / reject`。acceptでもrights/production/publicは開かない。
bounded repairは変える次元とtimestampを限定し、successful packageを上書きせずnew identityへ出す。
rejectはこのpair/thesis/directionを閉じるが、基盤コードやsource一般への否定には拡張しない。

同一マシンの入口:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\s1_two_source_common_context_probe_20260726\review\clip_s1_two_source_common_context_probe_v001\review\open_preview.ps1
```

## OUT-13との関係

OUT-13 Candidate 005は`M6_CLOSED_DENY_EXACT_ARTIFACT`のまま。内部editorial acceptanceと
technical provenanceを保持するread-only archive evidenceであり、public/monetized/
production/publish/upload/release候補へ戻さない。

S1は別artifact ID、二source、別question/thesis、別range inventory、別MP4 SHAを持つ。
したがってCandidate 005 denyの改名迂回ではない。一方、S1もrights approvalを得ておらず、
public/monetized/production/uploadはfalse。OUT-13のacceptanceやdenyをS1へ自動継承しない。

## portable境界

| 対象 | portability | 現在の役割 |
|---|---|---|
| CLI/render/tests/docs | Git portable | 開発・再検証 |
| artifact ID/hash/contract | Git portable | exact identity handoff |
| source media/caption local inputs | non-portable | same-machine build evidence |
| final MP4/review page/evidence JPEG | non-portable | same-machine S4 target |
| OUT-13 Candidate 005 | non-portable archive | deny済みpredecessor evidence |

`episodes/`はignoredかつtracked 0件。protected R3 previewも保持している。

## 先へ進む条件付き目標

| 段階 | 目標 | 開始条件 | exit evidence | owner |
|---|---|---|---|---|
| S4 Common-context review | 論としての成立を判断 | exact S1 package | SHA-bound verdictと四問回答 | User/Supervisor |
| S5 Bounded closure | accept/repair/rejectを正本化 | S4回答 | receipt、必要ならnew identity | Agent |
| S6 Second-pair repeatability | 一例の偶然成功を減らす | S5 accept + 実施承認 | 別pairの成功/失敗証拠 | Product owner |
| S7 Fresh rights inventory | 使用二source/rangeだけ再棚卸し | S5 acceptまたは対象固定 | material/range/terms/unknowns packet | Rights owner |
| S8 Rights/publication decision | intended useを人間が判断 | S7 + exact use proposition | allow/deny/restrictとpublication decisionを分離 | Rights/Public owner |
| S9 Production subtitle design | caption/commentary/attributionをdelivery仕様化 | S8のallow範囲 | font/license/safe-area/visual receipt | Designer |
| S10 Production render profile | codec/audio/device/color/QCを確定 | S9 | delivery manifestとdevice QC | Production owner |
| S11 Episode acceptance pack | lineageと全receiptを一束化 | S5/S8/S9/S10 | no-scope-widening manifest | Supervisor |
| S12 Thumbnail/metadata | rights-cleared素材でhuman choice | S11 | selected candidate、credit、restrictions | Human/Agent |
| S13 External-state dry-run | 変更前にidempotency/rollbackを証明 | S12、credential未使用 | upload plan、rollback、visibility plan | Agent |
| S14 Private/unlisted delivery | 限定公開で導通 | credential/visibility明示承認 | upload receipt、readback、rollback | Human owner |
| S15 Public release decision | public化を個別判断 | 全receipt + final owner | explicit release decision | Human owner |
| S16 Multi-episode operations | queue/retry/retentionを安定化 | 成功例・失敗例複数 | failure isolation、SLO、retention evidence | Agent/Operator |
| S17 Quality feedback loop | 人間判断を次planへ安全に反映 | S16 | dimension-specific trend、no silent policy promotion | Supervisor |
| S18 Sustainable platform | rights/quality/costを継続監査 | S16/S17 | audit cadence、owner map、rollback drills | Product owner |

generic N-source architectureはS6前に作らない。二source routeが一度通っただけでは、source数を
抽象化する根拠が不足する。公開価値を急ぐ場合もS7/S8を飛ばさない。

## 次に推奨する取っ掛かり

- **Advance**: S4四問に限定してexact videoをreviewする。意味判断が閉じるとS5へ進める。
- **Verify**: remote branch parityとpackage SHAを再確認する。別端末のcode-ready handoffが強くなる。
- **Audit**: source/range rights unknownをread-onlyで表にする。S4とpermission判断を混ぜずにS7準備ができる。
- **Explore**: S4後のsecond-pair候補だけを比較する。取得・render・framework化は開始しない。

今回のdrift監査では、実装なしにdocsだけ増えている状態ではない。current implementationと
exact packageが存在し、docsの主目的はstale OUT-13 next actionをlive S1へ合わせること。
残るリスクは、人間のS4 verdictがまだなく、一例からgeneric architectureへ広げる誘惑がある点。
