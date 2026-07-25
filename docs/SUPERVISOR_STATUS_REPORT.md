# OUT-13 main 統合・baseline 検証報告

更新日: 2026-07-25 JST

対象: ClipPipeGen のみ

## 監修時に最初に押さえる結論

OUT-13 は M4 の main 統合と M5 の integrated baseline verification を完了した。
明示 authority `clip-out13-main-integration-authorization-20260725-01` に従い、
`origin/main` の開始点 `5d6f69a64d510508a1f78ab3111a7780913a019c` から、受領済み
feature revision `18641fe917b084259869263e8db05d78325aa2db` までを
fast-forward した。squash、merge commit、force、履歴改変は行っていない。

M2 の人間受領は exact final MP4 SHA
`a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5`
に bind したまま維持している。受領 receipt 自体は acceptance 時点の記録なので、
内部の `main_integration_approved=false` を書き換えない。現在の main 統合 authority と
実行結果は `docs/RUNTIME_STATE.md` と `docs/CURRENT_HANDOFF.md` が担う。

次の開発入口は M6 rights readiness packet の準備だけである。rights judgment、
production subtitle/design/render、production image quality、thumbnail、publishing、
credentials、upload、private delivery、public release、deployment は開始も承認も
していない。

## 統合した Git identity

| 対象 | exact value | 判定 |
|---|---|---|
| integration start | `5d6f69a64d510508a1f78ab3111a7780913a019c` | fetch 後の `origin/main` |
| accepted feature | `18641fe917b084259869263e8db05d78325aa2db` | remote parity 済みの受領対象 |
| topology before integration | `origin/main...feature = 0 15` | main 側の取りこぼしなし |
| method | `git merge --ff-only 18641fe...` | 非破壊 fast-forward |
| accepted tree | `c8200d46214b01f5cd074cdcd37133089d92ab00` | integrated main tree と一致 |
| integration authority | `clip-out13-main-integration-authorization-20260725-01` | exact feature / one closure commit / one normal push |
| final revision | `refs/heads/main` | closure commit SHA の自己参照を避け、Git を正本にする |
| M5 verified tree | `refs/heads/main^{tree}` | closure docs と generated surfaces を含む最終 tree |

受領済み revision は最終 main の祖先でなければならず、統合後の feature tree は
`18641fe...^{tree}` と同一である。closure 記録は product implementation を変えない
一つの論理 commit とし、その exact SHA、push 結果、remote parity は Git readback と
最終 handoff で報告する。

## M2 artifact と判断境界

| 項目 | 記録値 | 意味 |
|---|---|---|
| artifact_id | `clip-out13-editorial-video-candidate-v1-005` | accepted package revision |
| repo_relative_path | `docs/output_layer/out13_human_acceptance_receipt.json` | tracked acceptance authority |
| open_command | `Invoke-Item docs\output_layer\out13_human_acceptance_receipt.json` | portable receipt の確認 |
| human entrypoint | `episodes/out13_editorial_video_candidate_20260723/review/out13_editorial_video_candidate_v005/review/index.html` | verified host 限定の ignored/private review surface |
| media identity | 82,594,810 bytes / 128.833333s / 1920x1080 / H.264 High + AAC / SHA `a76bab...bbb5` | 人間判断の exact target |
| verdict | `accept` | internal full-view editorial / visual review |
| review context | `out13_candidate_005_internal_full_view_editorial_visual_review_v1` | receipt の判断文脈 |
| accepted dimensions | composition、flow、subtitle presentation、内部用途の picture / audio quality | 受領が成立した範囲 |
| receipt SHA | `a0b14cdc0d294116775c9183499309bd7ad593a6373a556c11b334d2ac04b095` | tracked receipt の exact bytes |

同じ media SHA、review context、requested dimensions なら人間 review を再開しない。
package / implementation revision だけの変更でも再審査へ戻さない。media SHA が変わる、
または変更が accepted dimension に因果的に影響する場合だけ、新しい identity または
bounded review を起票する。

Candidate 003、004、005 は今回 read-only とした。各 package の inventory と accepted
MP4 SHA を統合前後で照合し、preview session、package、plan、caption、manifest、MP4 を
更新・削除していない。`episodes/` は ignored のままで、tracked file は 0 件である。

## M4 と M5 で確定したこと

| 作業 | 目的 | 効果 | 現在状態 | 次の動き |
|---|---|---|---|---|
| remote convergence | main と feature の exact ancestry を固定 | stale base や別 tip の統合を防止 | 完了 | final main parity を readback |
| M4 fast-forward | accepted feature だけを main へ移す | 15 commits の identity と履歴を保持 | 完了 | closure commit 以外の追加変更なし |
| canonical state repair | Runtime / Handoff / README / supervisor docs を同じ状態へ揃える | current capsule と next action を単一化 | 完了 | M6 まで status を進めない |
| dashboard regeneration | machine-readable current focus を docs と一致させる | 監修 AI が current gate を portable に読める | 完了 | generated drift を test で拒否 |
| M5 full validation | integrated final tree の回帰を確認 | feature 単体 green から main baseline green へ昇格 | 合格 | M6 readiness だけ提案可能 |
| privacy / artifact boundary | private media と tracked code/docs を分離 | Git に episode media を持ち込まない | 合格 | private/artifact-store 方針の承認までは維持 |

M5 は configured Python suite、OUT-13/current-authority focused suite、dashboard
generator、Python compile/static check、Node dependency/smoke、diff hygiene、
accepted ancestry/tree identity、tracked media と sensitive-data scan を最終 tree に
対して実行する。合格条件はすべて green、`git ls-files episodes` 0、accepted revision
が final main の祖先、closure 後の worktree clean、push 後の local/main parity 0/0 である。

## canonical surface の役割

- `docs/RUNTIME_STATE.md`: live state、M4/M5 verdict、単一 next action の正本。
- `docs/CURRENT_HANDOFF.md`: 別 terminal / 監修 AI が main から再開する最小手順。
- `docs/output_layer/out13_human_acceptance_receipt.json`: M2 の不変な判断記録。
- `docs/dashboard/project-status.json`: current focus の machine-readable projection。
- `docs/RUNTIME_HISTORY.md`: M3 authority repair と M4/M5 closure の履歴。
- `docs/decision-log.md`: integration authority、実行方式、未承認 gate の決定記録。
- `docs/idea-ledger.md`: M6 以降を dependency order で管理する backlog。

最終 commit SHA はその commit 自身の tree に埋め込めないため、
`final_main_revision_locator=refs/heads/main` と
`m5_verification_tree_locator=refs/heads/main^{tree}` を使う。handoff 時の exact SHA は
Git readback から提示し、tracked docs に placeholder を残さない。

## 未承認 gate

| gate | 現在状態 | 開くために必要なもの |
|---|---|---|
| rights / material use | pending | source/range 別の条件、判断 owner、allow/deny receipt |
| production subtitle design | false | font/license、safe area、exact visual review |
| production render | false | delivery codec/color/audio/device QC profile |
| production image quality | false | delivery context の visual QC と人間判断 |
| thumbnail | false / parked | accepted video 群、比較候補、人間 selection |
| publishing metadata | not approved | title/description/attribution/visibility decision |
| credentials / OAuth | not authorized | user-managed credential gate |
| upload / private delivery | not attempted | idempotency、rollback、visibility readback |
| public release / deployment | not approved | rights、production、publishing の owner receipts |

M4/M5 の技術的 green は、これらの判断または外部公開を代替しない。

## 可能な限り先までの条件付き目標

| 段階 | 目標 | exit evidence | 現在状態 / owner |
|---|---|---|---|
| M0 Remote convergence | feature を remote 最新へ同期 | feature parity 0/0、main ancestry | 完了 |
| M1 Exact artifact convergence | plan/input/package/media を照合 | SHA、bytes、digest、HTTP/readback | 完了 |
| M2 Internal editorial acceptance | exact media を全編判断 | user receipt、scope、dimensions | 完了 |
| M3 Main-integration preflight | branch 全差分と境界を監査 | repaired canonical state、READY verdict | 完了 |
| M4 Explicit main integration | accepted feature を main へ非破壊統合 | authority、fast-forward、ancestry | 完了 |
| M5 Integrated baseline verification | final main tree を再検証 | full/focused suites、smokes、privacy、parity | 完了 |
| M6 Rights readiness and decision | source/range ごとの判断材料を揃えて閉じる | owner、allow/deny/restriction receipt | 未着手。Rights owner / User |
| M7 Production subtitle design | internal 字幕を delivery visual へ上げる | exact frames、font/license、safe area verdict | M6 後。Designer / User |
| M8 Production render profile | 配信用映像音声仕様を確定 | codec/color/audio/device QC、output SHA | M6/M7 後。Production owner |
| M9 Episode acceptance pack | M6〜M8 の独立 receipt を束ねる | lineage-complete manifest | Supervisor |
| M10 Thumbnail and metadata | video 確定後に外装を作る | comparison set、selection、metadata draft | Human selection |
| M11 Private publish dry-run | 外部 state を変えず contract を検証 | dry-run receipt、idempotency、rollback | Agent + credential owner |
| M12 Private/unlisted delivery | 限定公開で end-to-end を確認 | upload receipt、visibility readback | User |
| M13 Explicit public release | 公開判断を監査可能に閉じる | rights/production/publishing owner receipts | User final gate |
| M14 Multi-episode operations | queue/retry/retention を複数 episode で証明 | isolation、SLO、quality trend | Operations owner |
| M15 Policy-constrained autonomy | 反復作業を安全に委譲 | allowlist、budget、stop conditions、audit log | Supervisor / User |

M6〜M15 は条件付き提案であり、FEATURE status や gate を自動変更しない。最短 critical
path は `M6 rights -> M7 subtitle design -> M8 render profile -> M9 episode pack`。
publish 系は M9 完了後も owner の明示判断を必要とする。

## 次に推奨する取っ掛かり

- **Advance**: M6 rights readiness packet を source/range 単位で作る。判断 owner と
  不足証跡が明確になり、rights decision を安全に起票できる。
- **Audit**: accepted receipt、source/material ledger、rights evidence の参照整合だけを
  read-only 監査する。制作成功と利用許可の混同を早期に検出できる。
- **Explore**: M7 subtitle design の thin-slice exit criteria を作る。M6 を越えずに、
  font/license と safe-area review の必要証跡を先に定義できる。
- **Verify**: 別 checkout から `main` と current handoff を読み、private media 不在時の
  portable re-entry を確認する。監修 AI の再開摩擦を下げられる。

現在は単発 artifact を統合せず完了扱いする drift を解消し、次 consumer を Rights
owner / User に固定した。M6 scope/owner の明示 authority がない間は rights judgment や
production work へ進めない。
