# 監修AI向け現状報告 — 2026-07-22 remote sync / development readiness / long-range goals

更新日: 2026-07-22 JST

正本branchは`main`。今回の同期確認時点で`main` / `origin/main`は
`089f45a5ba72d60c807d5ceafa3772fc8f6040f4`、parity `0 0`、tracked `episodes/` 0件である。
`git fetch --prune origin`後の`git pull --ff-only`は`Already up to date.`で、リモートから追加で
取り込むcommitはなかった。監修AIは`docs/CURRENT_HANDOFF.md`からOUT-12の実装状態と判断境界を復元し、
本報告からこの端末での再検証結果と先行目標を判断できる。実sourceと生成mediaはGitへ含めず、
同一マシン証拠とportableなtracked証拠を分離する。

## この端末での同期・開発準備

2026-07-22 JSTにremote refsを更新してff-only pullを実行した。同期前後とも
`main...origin/main`、ahead / behind `0 0`、tracked worktree clean、untracked 0件、tracked
`episodes/` 0件である。依存はlockfileから再構築し、現在の実装入口を次の通り再検証した。

| 確認面 | この端末での結果 | 開発・監修上の意味 |
|---|---|---|
| JavaScript依存 | `npm ci`成功、23 packages追加、24 packages audit、脆弱性0 | `package-lock.json`どおりのElectron開発環境 |
| Python実装 | Python 3.11.0 / uv 0.10.0、`uvx --with Pillow pytest -q`で596 passed / 118.79s | OUT-09〜OUT-12を含む全suiteがlocal pass |
| GUI | `npm run smoke` / `npm run smoke:electron`ともにOK | Node側とElectron起動経路が利用可能 |
| media toolchain | FFmpeg / ffprobe 8.1.1、yt-dlp 2026.03.17を検出 | 新しい実sourceが用意されればOUT-12 routeを実行可能 |
| CLI入口 | `python -m src.cli.main build-real-video --help`成功 | source / intake identity、resume / force、review生成の引数を解決可能 |
| cleanup分類 | tracked/staged変更0、untracked 0、ignored 1,095（`episodes` 485、`node_modules` 609、`.claude` 1） | 保護対象preview、依存、別worktree metadataを消さずに開発可能 |

local artifact境界も確認した。OUT-12の`validation_readback.json`、final MP4、`review/index.html`は
この端末には存在しないため、`127.0.0.1:8075`を現在利用可能なreview URLとしては扱わない。一方、
cleanup policyで保護されたR3 `human_preview_session/`は34ファイル / 60,060,797 bytesで存在し、
cleanup対象から除外した。したがって現在は
**tracked codeの開発・テストは可能、OUT-12 exact mediaの再視聴だけは生成元hostまたはsource復元が必要**
という状態であり、remote handoffのportable / same-machine境界と一致する。

## 到達した状態

OUT-10 / OUT-11では5 sourceのShort候補をexact bytesへbindしてinternal acceptanceを閉じ、winnerを
選ばず、追加Short修復・再レビューを終了した。その入力境界からOUT-12を開き、取得済みの実source
一本をprovenance確認から長尺MP4、machine validation、localhost reviewまで一コマンドで処理する
vertical sliceを完成させた。状態は`AUTOMATED_REAL_VIDEO_PIPELINE_OPERATIONAL_V1`で、automation
acceptanceはtrue、人間内容レビュー待ちはfalseである。

`build-real-video`はsource fingerprint、content/scene/black/silence解析、chronological Timeline IR、
caption timing remap、H.264/AAC render、13項目validation、manifest、review packageをatomicに作る。
成功済みpackageは`--resume`でpayloadとfingerprintが一致するときだけ再利用し、不一致はfail closedに
する。異なる入力を上書き生成する場合だけ、意図を確認したうえで`--force`を使う。

## 現在のtracked exact artifact契約

| 面 | 確定値 | 監修上の意味 |
|---|---|---|
| artifact | `clip-out12-one-command-real-video-automation-v1-001` | OUT-12 automation acceptanceのidentity |
| source | `youtube:gUwJBRUIWow`; SHA `8decc04ddcd805cadb77100eb5f7cbf2dc9883a32cb42aba0ed4c216fd0037cf`; 260.643991s | 3分以上の実sourceとしてpreflight済み |
| timeline | 11 cut / 3 semantic sections / coverage 1.0 | full-source chronologyとsource mappingを保持 |
| output | 260.693767s; 1920x1080; H.264/AAC; 142,789,781 bytes | internal long-form実動画が生成済み |
| output SHA | `5d391ffd5ff48da03858d8f558ff680bd45643e108d765fefefceb32c250a584` | local artifactを再確認するときのexact identity |
| captions | 468 timing cues; overlap / negative / orphan 0 | timing/containmentのみ。歌唱・歌詞・speaker・意味は未主張 |
| signal | -14.15 LUFS; -1.44 dBTP; 最大隣接cut差1.27 LU; black 0.7007s; silence 0 | internal machine QA pass。production mix承認ではない |
| resume | 2.095s; analysis/caption/render/validation cache hit; render false;同一SHA | 高コスト処理のhash-verified再利用を確認 |
| review | HTTP 200 / Range 206; desktop/mobile overflowなし; initial paused/muted/time0; console/media error 0 | localhost reviewのaccessとsafe media stateを確認 |

review入口は生成元の同一マシンで`http://127.0.0.1:8075/review/index.html`。server停止後は次で
foreground再開する。この端末にはpackageがないため、ここでは実行しない。

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File episodes\out12_source05_one_command_real_video_20260721\review\out12_one_command_real_video_automation\review\serve_preview.ps1
```

## 実装と失敗修復の意味

初回runでAV stream duration差とtrue peak超過を検出したため、失敗証跡を消さずにcorrective passを
実行し、duration差0.008767秒、true peak -1.44 dBTPへ修復した。mobile review表のdocument overflowと、
Windows browserがRange requestを中断した際のserver traceも生成CSSとconnection handlingで直した。
いずれもSOURCE-05だけを通す手作業ではなく、次の実source runにも適用されるroute修復である。

この成果は作品内容の良否を自動判定したものではない。source-native baked textを保持し、caption authorityは
timing/containmentへ限定した。OUT-12の任意内容確認はできるが、automation acceptanceを再びreview待ちに
戻したり、意味・rights・production qualityを推論したりしない。

## 別端末へ移るものと移らないもの

| 対象 | Gitで移るか | 再開方法 |
|---|---|---|
| code / tests / authority docs / schemas | 移る | `main`をfetchしてff-only pull |
| exact artifact identity / validation数値 /判断経緯 | 移る | Runtime、Current Handoff、output contract、decision logを読む |
| source MP4 / final MP4 / contact sheet / waveform / localhost package | 移らない | 同一マシン`episodes/`を保持。別hostでは再取得・再生成または承認済みprivate transport |
| credentials / OAuth / upload state | 存在させていない | 新しい外部連携gateが承認されるまで作らない |

新しい端末では次を実行する。

```powershell
git fetch --prune origin
git switch main
git pull --ff-only
git status --short --branch
git rev-list --left-right --count 'HEAD...@{u}'
git ls-files episodes
```

期待値はclean worktree、parity `0 0`、tracked `episodes/` 0件。`episodes/`が空でもcode/context再開の
欠陥ではなく、media再検査だけが同一マシンまたは再生成を要求する。

## 可能な限り先まで見通した目標案

以下は実装承認ではなく、依存関係を見失わないためのgoal ladderである。各段階は前段の技術証拠を
再利用するが、human / rights / credentials / public gateを自動昇格させない。特にM2a〜M2cは別々の
判断面であり、並行準備はできても、一つのpassを他の承認として代用しない。

| 段階 | 解くbottleneck / workflowへの効果 | 着手条件 | 完了を示す最小証拠 | 現在状態 |
|---|---|---|---|---|
| M0: OUT-12 baseline保持 | 実sourceからreview packageまでの一縦糸を回帰基準にする | 現在のtracked code/docs/tests | accepted artifact identity、全suite pass、closed gate不変 | 完了 |
| M1: second-source repeatability | SOURCE-05固有の偶然を除き、次の実装判断を実測へ変える | 異なるprovider/identityの3分以上source、provenance/rights snapshot、別output dir | 同じCLIで新artifactを生成、13 validation passまたはstage別failure receipt、`--resume`同一SHA、source専用分岐を増やさない | proposed・最優先 |
| M1b: failure taxonomy v1 | AV sync、peak、black/silence、caption/native text、scene boundaryの修復判断を安定させる | M0とM1の比較可能なmanifest/readback | source固有観測と共通failure classを分離し、再試行可否・corrective pass上限・human escalation条件を契約化 | initial evidenceあり |
| M2a: production subtitle design gate | native baked text、追加字幕、font/license、line-break、安全領域、badge/話者表現を制作判断へ上げる | 明示されたdesign ownerと対象artifact | exact artifactへbindしたvisual acceptance receipt、font license/readback、表示ルールと非対象範囲 | closed |
| M2b: production render acceptance gate | internal H.264/AAC plumbingをdelivery可能な映像・音声仕様へ上げる | delivery profile、対象device、色/音量/QC閾値、M2aとの合成条件 | full decode、AV/color/audio/device QA、exact SHA、human production acceptance receipt | closed |
| M2c: rights/material-use clearance | 技術成功と利用許可を明示的に接続する | source identity、利用範囲、権利者/ガイドラインsnapshot、判断owner | source/rangeごとのallow/deny/restriction、証拠時点、reviewerを持つrights receipt | pending |
| M3: private artifact transport | 生成host以外でもsame bytesをreviewできるようにする | storage、暗号化/ACL、retention、削除/rollbackのowner承認 | manifestとhashを保ったupload/restore、second-host SHA一致、期限/アクセス監査、Gitにmedia 0件 | unapproved |
| M4: production candidate convergence | subtitle/render/rightsを一つのepisode identityへ束ね、何が未承認かを一画面で判断可能にする | M2a〜M2cの独立receipt、episode pack contract | gateを混同しないepisode manifest、accepted/rejected/deferred readback、再生成lineage | proposed |
| M5: thumbnail + metadata package | video完成後の手戻りを減らし、非公開delivery準備まで接続する | 3〜5本のaccepted実output、thumbnail再開判断、publish draft schema | 複数例で再現したcover contract、exact thumbnail acceptance、title/description/tags/category draft | parked / proposed |
| M6: private/unlisted delivery | OAuth後もpublic化せず、外部deliveryのidempotencyとrollbackを先に証明する | M2a〜M2cとM4/M5完了、credentials/OAuthの明示承認 | dry-run、private/unlisted upload、video ID、visibility/readback、thumbnail set、upload receipt、retry/rollback証拠 | 未実装・要承認 |
| M7: explicit public release | 制作・権利・公開判断を一つの監査可能なrelease decisionへ閉じる | M6 artifact、rights/production/thumbnail/metadataの全owner acceptance | public化前の最終decision packet、visibility/made-for-kids等の明示値、公開後receiptとrollback手順 | 将来gate |
| M8: multi-episode operations | 単発成功から継続運用へ移り、失敗episodeが他を止めないようにする | M1〜M7のcontractが安定 | queue/retry/observability、provider fallback、artifact retention、品質傾向、複数episode回帰、operator cockpit | long-range proposal |

critical pathは`M1 -> M1b -> {M2a, M2b, M2c} -> M4 -> M5 -> M6 -> M7 -> M8`である。M3は
cross-host reviewが必要になった時点でM2と並行できる。最終North Starは、複数episodeをsource intakeから
制作・権利・private deliveryまで再開可能に運び、public releaseだけは根拠付きhuman decisionで開く
半自動制作システムである。

## 次に選べる四つの入口

| 入口 | いま減らす摩擦 | 選ぶと次に可能になること |
|---|---|---|
| **Advance — M1** | OUT-12が一sourceの偶然かという最大の不確実性 | M1b failure taxonomyとproduction gate設計を実run比較に基づけられる |
| **Audit — M1b準備** | corrective passの再試行条件が暗黙であること | source取得を待たず、次runのfailure receiptとstop条件を先に定義できる |
| **Verify — M2c** | 技術artifactと利用許可が分離したままであること | production candidateへ進めるsource/rangeと、除外すべき範囲を確定できる |
| **Explore — M3** | OUT-12 exact mediaをこの端末で再検査できないこと | Gitを汚さずsecond-host reviewと監修の再現性を得られる |

現在の推奨は`Advance — M1`。別source一本を同じCLIで処理すると、OUT-12の最大の残余不確実性を
最小範囲で測れ、その後のfailure taxonomyとproduction acceptance設計の質が上がる。対象sourceをまだ
決めない場合は`Audit — M1b準備`が安全な次点である。rights、production subtitle/design/render、
thumbnail、winner、public/publishing、uploadは依然として別owner gateで、本handoffやinternal
validationから承認を推論しない。

## 監修AIが維持する境界

- 正本は`main`と`docs/RUNTIME_STATE.md` / `docs/CURRENT_HANDOFF.md`。古いresume capsuleをcurrent扱いしない。
- OUT-10 / OUT-11のaccepted exact bytesとOUT-12 automation acceptanceを、理由なく再審査へ戻さない。
- `episodes/`をtrackせず、`git ls-files episodes`を0件に保つ。
- source textから歌唱、歌詞、speaker identity、rightsを追加推定しない。
- gateを一括で開かず、目的とacceptanceが明示された一つのsliceだけ進める。
