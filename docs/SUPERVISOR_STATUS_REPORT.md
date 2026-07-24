# 監修AI向け現状報告 — 2026-07-24 remote同期・開発再開・長期目標提案

更新日: 2026-07-24 JST

対象: ClipPipeGenのみ

active branch: `codex/out-13-editorial-video-candidate-v1`

## 監修時に最初に押さえる結論

remoteの最新6 commitをlocalへfast-forwardし、OUT-13 v4の強化実装、tests、handoff docsを
取得した。Node依存はlockfileから再構成済みで、GUI / Electron smoke、OUT-13 CLI help、
Python全体回帰を実行した。同期時点のWindows環境でだけ露呈したjunction検出2件は、
reparse-point判定を実装して修復した。tracked codeは開発継続可能である。

ただしremote文書の「Thank端末にcandidate 005が存在する」という記録は、
現在の`DESKTOP-U9P4LKJ` checkoutには当てはまらない。candidate 004 / 005のreview package、
MP4、validation、launcher、candidate 005 planは不在で、現在のsource / transcript /
rights bytesも005契約値と異なる。従ってhuman editorial reviewを直ちに開くことはできない。
Gitでportableなのはbuilder / tests / docs / contractまでであり、次の実作業は
exact private recoveryまたはnew identity rebuildの二択である。

OUT-13のmachine receiptは失われたと断定しない。source host上で成立した
candidate 005のSHA・manifest・browser QAは履歴証拠として保持しつつ、
このcheckoutのlive availabilityとは分離した。rights、production subtitle/render、
thumbnail、publishing、upload、public releaseはいずれも未承認のままである。

## remote同期とbranch topology

開始時HEADは`558f681`、upstreamは6 commit先の`673da5d`だった。
`git fetch --prune origin`後、次のff-only pullで競合なく取り込んだ。

```powershell
git pull --ff-only origin codex/out-13-editorial-video-candidate-v1
```

取り込んだ範囲は`da58a82..673da5d`で、主な意味は次の通り。

| remote変更 | workflowへの効果 | このcheckoutでの扱い |
|---|---|---|
| immutable output / sibling journal | 成功packageをfailureやresumeで汚さない | code / testsを取得しWindows junctionも補強 |
| signed PCM lineage | equal-energy別波形等をauthorityとして誤受理しない | tracked testsで再検証 |
| caption acquisition receipt | provider IDとexact JSON3 bytesをplan記述だけに依存せず結ぶ | source-host receiptとして保持 |
| closed manifest / link rejection | package外bytesの間接参照を防ぐ | Windows reparse pointも拒否するよう修復 |
| candidate 004 / 005 handoff | exact review targetと未承認gateを別端末へ伝える | package不在をlive再判定し、handoffを訂正 |

同期直後のbranch / remote parityは`0 0`、`origin/main...HEAD`は`0 10`、
`origin/main`は`5d6f69a64d510508a1f78ab3111a7780913a019c`だった。
OUT-13はmain未統合である。この報告とWindows修復を含むcommitが次のremote resume tipになる。

## worktree・依存・artifact衛生

開始時のtracked / untracked worktreeはcleanだった。ignored stateを次の5種類へ分けた。

| 区分 | live確認 | 処置 |
|---|---|---|
| active-scope tracked files | なし、remote同期後に本作業差分のみ発生 | 本commitへ集約 |
| unrelated tracked modifications | なし | 復元不要 |
| untracked files | なし | 削除不要 |
| Python / pytest cache | `.pytest_cache`と各`__pycache__` | path限定`git clean -fdX -- <paths>`で整理 |
| retained / required ignored state | `episodes/`、`node_modules/`、`.claude/worktrees/` | 一括cleanせず保持 |

`git ls-files episodes`は0件。cleanup policyで保護される
`episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/human_preview_session/`
は存在し、削除していない。candidate mediaをGitへ追加していない。

`npm ci`は23 packagesを再構成し、24 packagesをaudit、脆弱性0。
実行環境はNode `v22.19.0`、npm `10.9.3`、Electron `42.0.0`、
local Python `3.11.0`、uv `0.10.0`。Python検証はproject既定どおり
`uvx --with Pillow`で隔離環境を使った。

## 検証結果と今回閉じた回帰

| command | 結果 | 判断 |
|---|---|---|
| `npm run smoke` | `gui smoke: OK` | GUIのread-only/current wiringは起動可能 |
| `npm run smoke:electron` | `electron smoke: OK` | Electron shellを現lockfileで起動可能 |
| `uvx --with Pillow python -m src.cli.main build-editorial-video-candidate --help` | exit 0、必須`--artifact-id`を表示 | OUT-13 CLI contractへ到達可能 |
| 初回`uvx --with Pillow pytest -q` | 652 passed / 2 failed | Windows junctionをPython 3.11の`Path.is_symlink()`だけで検出できない |
| junction targeted tests | 2 passed | `st_file_attributes & FILE_ATTRIBUTE_REPARSE_POINT`で修復を確認 |
| 最終`uvx --with Pillow pytest -q` | 654 passed | tracked全体回帰green |

初回失敗は仕様期待の誤りではなく、Windows directory junctionが
`Path.is_symlink()`でfalseになるruntime差だった。これによりrun journal aliasが拒否されず、
manifest validatorも「symlink禁止」より後のpackage escapeで止まっていた。
`os.lstat()`のWindows file attributesを読む補助判定を追加し、Python 3.11でも
symlink / junction / other reparse pointをlink-like targetとして先に拒否する。
package immutability、journal isolation、external target禁止というOUT-13 v4 contract自体は変えていない。

## source-host receiptと、このcheckoutの実在を分ける

source hostが記録したcandidate 005は次のmachine receiptを持つ。

| receipt面 | source-host記録 | acceptance境界 |
|---|---|---|
| identity | `clip-out13-editorial-video-candidate-v1-005` | human受理済みではない |
| timeline | 7 cuts / 5 sections / 8 omissions / 128.795s | semantic selection受理ではない |
| final media | 128.833333s、82,594,810 bytes、SHA `a76babda...bbb5` | production/public-readyではない |
| caption | provider JSON3 102 cues、mapping 1.0、split/duplicate/missing 0 | 公式著者性・speaker意味は主張しない |
| package | 25 files / 87,123,995 bytes、tree digest `ed45fd4c...040` | Git portableではない |
| machine/browser | full validation、page 200、Range 206、overflow/error 0 | 人間全編視聴の代用ではない |

現在のcheckoutを`Test-Path`とSHAで読み直した結果は次の通り。

| local対象 | live result | candidate 005契約との関係 |
|---|---|---|
| candidate 004 / 005 root | `episodes/out13_editorial_video_candidate_20260723`自体が不在 | review / resume不可 |
| source MP4 | 56,063,684 bytes、SHA `e2206cef...2d18` | 契約`6f78657e...6103a`と不一致 |
| transcript | 42,735 bytes、SHA `ef928d4e...b42d6` | 契約`4a7b4fd8...3495`と不一致 |
| provider JSON3 | 40,303 bytes、SHA `3c15535f...9919` | 契約値と一致 |
| rights snapshot | 2,666 bytes、SHA `e6ea9471...64c12` | 契約`4302c4a1...bb8`と不一致 |
| `editorial_plan_input_v005.json` | 不在 | 同一fingerprintを再現不可 |
| protected R3 preview | 存在 | cleanup保護継続 |

この差により、tracked docsの旧`human_entrypoint`、`review_open_command`、
`machine_readback`はcurrent surfaceから外した。source-host receiptは
`docs/output_layer/OUT_13_EDITORIAL_VIDEO_CANDIDATE.md`に残し、現在の実在を示す
`RUNTIME_STATE` / `CURRENT_HANDOFF` / dashboardではlocal unavailableを正本とする。

## 現在のシステム到達点

ClipPipeGenは既に、rights / material ledger / source acquisition / transcript /
cut context / subtitle draft / NLE CSV / diagnostic render / explicit editorial plan /
manifest / review packageをepisode単位でつなげられる。OUT-12は取得済み実source一本を
一コマンドで長尺review packageへ運び、OUT-13は人間が定義した非連続editorial planを
caption evidence付きで同じreviewable videoへ運ぶ。

まだ製品化を止める主なbottleneckは、render機能の有無ではない。

1. ignored local artifactが端末を跨がず、review consumerへ届かない。
2. human editorial verdictがexact SHAへbindされていない。
3. rights owner receipt、production subtitle design、delivery render profileが独立に未完了。
4. thumbnail / metadata / publishingはvideo acceptanceへ接続されていない。
5. 複数episodeでqueue、retry、retention、品質傾向を測る運用層がない。

## 監修AIへ提案する最遠目標

以下は依存順を明示したproposalであり、FEATURE statusを自動で`approved`へ上げない。
各段階は前段のacceptanceを推定せず、観測可能なexit evidenceで閉じる。

| 段階 | 目標 | 最小exit evidence | 解消する摩擦 / 次に可能になること |
|---|---|---|---|
| M0 再開基盤 | remote同期・依存・回帰・handoffをgreenにする | branch parity、lockfile install、full suite、正しいlocal availability | 別AIが誤った入口から始めない |
| M1 Artifact Transport v1 | exact inputs / plan / packageをprivateに移送・照合できるcontract | inventory、hash、size、source-host/receiver receipt、rollback、Git非追跡 | host依存を解き同一SHA reviewが可能 |
| M2 OUT-13 Editorial Closure | candidate 005またはnew identityを人間がaccept/repair/reject | final SHA、reviewer、timestamp、bounded findings | semantic/editorial品質をbranch acceptanceへ接続 |
| M3 Main Integration | OUT-13 v4をmainへ統合 | merge preflight、full regression、main parity、migration note | 後続sliceが安定API上で開発可能 |
| M4 Rights Decision Packet | source/range/useごとの利用判断をownerへ渡す | guideline snapshot、source intervals、owner allow/deny/restriction receipt | internal artifactをproduction検討へ進められる |
| M5 Production Subtitle System | typography / license / safe area / speaker policyをproduction化 | design tokens、font license、stress set、desktop/mobile/TV human receipt | diagnostic字幕からdelivery字幕へ移行 |
| M6 Production Render Profile | codec / color / audio / device QCをdelivery仕様へ固定 | versioned profile、deterministic render、decode/seek/color/audio QC、human acceptance | public-ready候補を技術的に生成可能 |
| M7 Episode Acceptance Pack | M2/M4/M5/M6の独立receiptを一identityへ束ねる | immutable episode pack、gate matrix、lineage、rollback map | 「何が承認済みか」を一画面で判断可能 |
| M8 Thumbnail + Metadata | accepted videoから比較サムネとmetadata draftを作る | 3–5 alternatives、selection receipt、title/description/tags draft | 投稿準備の手戻りを削減 |
| M9 Private/Unlisted Delivery | OAuth / retry / idempotencyを公開前に証明 | explicit credential approval、private/unlisted upload receipt、rollback test | publishing integrationを低リスクで実証 |
| M10 Explicit Public Release | visibility / thumbnail / metadataを明示判断で公開 | rights+production+publishing owner receipts、final confirmation、audit log | 一episodeの制作→公開loopを閉じる |
| M11 Multi-Episode Operations | queue / resume / retry / retention / alertを複数episodeで運用 | 3–5 episode run、failure isolation、SLA/quality dashboard | 継続制作のoperator負荷を測定・削減 |
| M12 Quality Learning Loop | acceptanceと修復をsource/preset別に分析する | structured findings、false-positive率、repair率、lead time trend | 自動化を人間判断の実績から改善 |
| M13 Controlled Scale-out | provider / format / languageを増やす | provider adapter contract、cost/privacy/rights review、cross-source regression | 単一pilot依存から再利用可能な制作基盤へ移行 |

長期のNorth Starは「自動で動画を作る」ことだけではない。
`source identity -> rights/material evidence -> editorial decision -> production assets ->
publishing receipt`を一つのepisode lineageにし、どのgateが誰の判断で開いたかを再現できること。
自動化率は、human reviewの探索時間、再生成回数、artifact紛失、公開前差し戻しを減らせる範囲で上げる。

## 推奨する次の取っ掛かり

| 入口 | 今解くbottleneck | 選ぶと次に可能になること |
|---|---|---|
| **Advance — private recovery** | candidate 005のexact bytesがこの端末にない | 同一SHAを維持したhuman editorial review |
| **Explore — new identity rebuild** | recovery経路を使わない場合の停止 | 現在の入力authorityで006以降を作りreviewを再開 |
| **Audit — Artifact Transport v1** | same-machine evidenceの再発リスク | 今後の候補を端末移動可能なreceipt付きpackageにする |
| **Verify — main integration preflight** | branchがmainより先行したまま後続開発が積み上がる | editorial closure直後に安全にmainへ統合 |

優先順位は`M1またはnew identity rebuild -> M2 -> M3`。
M4 rightsとM5/M6 productionはM2後に並行設計できるが、M8以降を先に実装すると
未受理videoへthumbnail / publishing作業がぶら下がり、手戻りが増える。

## 監修AIが判断すべき現在の二択

| 選択 | 必要条件 | 長所 | 注意点 |
|---|---|---|---|
| candidate 005 private recovery | source hostまたは承認済み保管先へアクセスできるowner | 既存SHA・machine receiptを保ち最短でreview可能 | private media移送の明示承認とhash照合が必要 |
| candidate 006+ rebuild | 現在のsource/transcript/rightsを新authorityとして採用し、新planを作る | source host依存を解きこの端末で再現できる | 005の復元ではなく別artifact。semantic planの再判断が必要 |

どちらを選んでも004 / 005は上書きしない。review対象が成立するまでは
human acceptance、rights、production/public readinessを進めたと報告しない。
