# OUT-14 Push Micro-Arc Editorial Reconstruction v2・監修引継ぎ報告

更新日: 2026-07-27 JST
対象: ClipPipeGen のみ
mission: `CPG-OUT14-PUSH-MICROARC-EDITORIAL-RECONSTRUCTION-V2`

## 現在の結論

`clip-out14-push-microarc-editorial-v2-001`は
`OUT14_PUSH_MICROARC_EDITORIAL_V2_READY_FOR_HUMAN_REVIEW`。
final MP4 SHAは
`8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414`、
406.55秒、1920x1080 H.264/AAC。Discordプロフィール変更が全体通知になった出来事を
8 cutで因果順に再構成し、actual-audio transcript 142 cue、構成telop 4本、
title 3案、実source frame thumbnail roughを一つのreview packageへ束ねた。

機械検証と代表フレーム目視はgreen。人間による全編editorial / language /
title / thumbnail rough acceptanceは未実施。rights、production subtitle/font、
production render、YPP、upload、publication、visibilityは閉じたまま。

## remote同期と作業境界

| 対象 | 実施内容 | 現在状態 |
|---|---|---|
| fetch | `git fetch --prune origin` | `origin/main` exact `edb782acd1e06aca46e0a5d10295ea52f30ad5c7` |
| exact base | mission指定 `30b4891399ad474b624518f7dcb76591b68c8bef` | object存在、origin/mainの1 commit先 |
| isolated worktree | branch `codex/out14-push-microarc-editorial-v2` | requested pathで開発 |
| original checkout | v1 exact base worktree | 開始時clean、書込みなし |
| remote mutation | push / PR / merge | 未実施・未承認 |
| media | `episodes/out14_push_microarc_editorial_v2_20260727/` | ignored local evidence、tracked 0 |
| protected evidence | v1、S1、Candidate 003/004/005、M2、M6 | 開始・終了SHA一致、上書きなし |

private mediaはローカルだけに存在する。tracked code/docsだけでは別hostでexact MP4を
再現できない。fresh-clone reproducibilityは別gateであり、今回のsame-host successから推定しない。

終了時の保存照合は次のとおり。

| protected identity | 終了時SHA-256 | 判定 |
|---|---|---|
| v1 final MP4 | `1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f` | 開始値一致 |
| v1 manifest | `73233c19726c4f02672630167793f437dbff6dd81a0d361ab942b8ce20d8bff4` | 開始値一致 |
| v1 source | `5e026c94f40acd0dfc32a5ab610300a7bccbe3cd66441a7d9cc703cc7b83d240` | 開始値一致 |
| S1 final MP4 | `dc621bfe4be95b1fcc22204942e744d3a4a5dd56600bd8987b7cb6f5b55f95be` | contract値一致 |
| Candidate 003 / 004 / 005 final MP4 | `a76babda8b24335635ab048a9a5389d892c2761dd1598cd5b9c6c22ab758bbb5` | 3件とも開始値一致 |
| M2 acceptance receipt | `881036c3b90303d0147223a974ebf9e8e7f471d3d9155f9fc11279c72d733a95` | tracked diff 0 |
| M6 decision packet | `1e9570c5598203df6367bbb62b4b916c16c04c058a7e144837fb1b352292d355` | tracked diff 0 |

## v1 の人間判断をどう保存したか

v1 final SHA `1db41c4f0f36b45ff5cdbf4c681a69054e75478bb4d925a666d223d454c4d07f`
のtechnical passは履歴として保持した。同じexact identityに対する人間判断は`rejected`。

| 指摘 | v2での処理 |
|---|---|
| 連続11分の字幕付き抜粋に見える | 8つの意味cutと4本の可視telopへ再構成 |
| episode境界が見えない | setup / escalation / notification / endingをcreator telopで表示 |
| 字幕が遅い | actual-audio word timingからdeterministic mapping、24 anchorで検証 |
| 「猿と喧嘩」「アライグマ」誤認 | v1 source span overlap 0、既知2 locusをreadbackで完全除外 |
| 非発話annotation | viewer-facing count 0をgate化 |
| funeral/deathの主要hook回避 | C1をhard-gate reject、active quarantineへ固定 |
| source-frame thumbnail rough | 1280x720と320x180をactual selected bytesから生成 |

decision recordは
`docs/output_layer/OUT_14_V1_HUMAN_EDITORIAL_DECISION.json`。
quarantine `out14-contiguous-auto-caption-unstructured-v1`は`ACTIVE`。
cosmetic changeだけではquarantineを脱出できない。

## 候補探索と競合確認

3本のpublic completed streamを匿名でreconし、9 episode candidateを作成した。
one-sentence premise、closed causal arc、sensitivity、quarantine、chronology、
anonymous source、actual-audio transcript feasibilityをscore前hard gateにした。
hard-gate passだけを100点rubricで比較した。

| candidate | 話題 | score / gate | 結果 |
|---|---|---:|---|
| C1 | v1帰省・葬儀・動物 | sensitivity/quarantine fail | reject |
| C2 | お化け屋敷 | 79 | coverage過密 |
| C3 | Discordプロフィール通知 | 93 | selected |
| C4 | 夏祭り | 79 | coverage過密 |
| C5 | ホテルの出来事 | 87 |既存coverageが強い |
| C6 | 家族・先生の謎解き | 75 | hook/payoff理解が弱い |
| C7 | ジェットスキー | 88 | strong clipsが占有 |
| C8 | 巨大スイカ | 70 | causal payoffが薄い |
| C9 | ニコ関連 | sensitivity/closed payoff fail | reject |

競合recordは11件。各URL、title、channel、公開日、duration、views、likes、
comments、channel scale、same/adjacent分類を保存した。starting locatorの19件という値は
operator-suppliedで、live endpoint 403のためlive-confirmedへ昇格していない。

## source と時刻原点

selected sourceは`youtube:rltNvZ_FY8Q`。匿名format inventoryで1080p60を確認し、
format `399+251`を選択した。取得窓はprovider 2268–2910秒、
1920x1080/60 AV1 + Opus、642.001秒、97,061,823 bytes、
SHA `335e9a131fae06b716bd7ac479e914fb849be117b15c4b412c9b4c565fef264e`。
cookies、OAuth、credentialは使っていない。

窓の0秒がprovider 2268秒と一致することを、protected v1 source audioの2250–2295秒と
selected窓冒頭24秒を200Hz mono PCMにしてnormalized cross-correlationで測定した。
最大相関0.859306、絶対開始2268.03秒、要求との差+30ms。renderの
`source_media_offset_seconds`へ2268.03を使用した。

## actual-audio transcript と字幕

selected actual audioをfaster-whisper 1.2.1 / small / CPU int8 / word timestampsで処理。
provider JSON3は候補発見・比較仮説・provenanceに限定し、viewer-facing authorityにしていない。
Discord、おかゆ、遊戯王、みこめっと、みこち、すいちゃん、蒙古タンメン、
プロフィール、ステータス等の明白な固有語・system termを文脈校正した。

単語時刻でcut境界を越える語を除外し、最大16文字のcueへ再構成。固有語は不可分単位として
mergeしてからcue分割する。初回目視で見つけた`Discor / d`分割を回帰テスト化し、
最終実フレームでは`Discordってさぁ使ってる`が一行に収まった。

| timing gate | 結果 |
|---|---:|
| anchors | 24 / required 24、各section 3 |
| rendered median signed onset error | 0.0ms |
| rendered absolute p95 | 0.0ms |
| provider diagnostic median | -210.5ms、authorityなし |
| viewer-facing non-speech annotation | 0 |
| presentation | 142 cue、overflow/3-line/overlap/negative/orphan 0 |

0msは人間が全語の音素開始を再採点した値ではなく、actual-audio ASR word onsetを
deterministic cut offsetへ運んだmapping error。言語・知覚acceptanceは人間gateに残る。

## 構成、title、thumbnail

selected cutsはprovider clockで
2276.48–2326.76、2392.92–2457.80、2468.88–2521.44、
2556.20–2632.48、2645.20–2737.28、2775.40–2806.00、
2841.24–2861.00、2886.32–2906.40秒。chronologyは変更していない。

editorial telopは
`Discordのプロフィールを変えた朝`、
`遊びで変え続けた結果`、
`変更通知が届いていた`、
`変更は全体通知される`。
speechとは別namespace・別provenance。

working title:
`Discordのプロフィールを遊びで変えたら、全スタッフに通知が飛んでいた`

alternatives:

- `おかゆとプロフィールをいじった結果、通知先に戦慄するスバル`
- `「蒙古タンメン スバル」が全スタッフに共有された朝`

thumbnail roughはprovider 2688.44秒のactual source frameへ
`全スタッフに通知`を重ねたreview補助。1280x720 SHA
`d0edde1236f8b254c1fe9588d1f656aef057f1baba603be55239d20c3170c3ce`、
320x180 SHA
`5bfa59b17320350b4286fb63f68e4427d2a6badc691cfcef960dcd01fb3e822e`。
generated imageではなく、publication thumbnail acceptanceも未判定。

## 最終メディアとreview package

| 検証 | 結果 |
|---|---|
| final media | H.264/AAC yuv420p、1920x1080、406.55秒、405,217,162 bytes |
| exact video SHA | `8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414` |
| full media checks | 13 / 13 pass |
| audio | -14.93 LUFS、-1.85 dBTP、最大隣接cut差0.82 LU |
| decode/signal | full decode、faststart、monotonic timestamp、A/V、black/silence pass |
| manifest | 29 payload rows、manifest SHA `774351a7fc55839e05e58276280570a27ac1fd0aa7fa78283cdcf79f5d8634a9` |
| package | manifest閉集合 30 files / 408,275,872 bytes |
| localhost | page 200、MP4 Range 206 / 1024 bytes |
| page order | title → actual-frame thumbnail rough → full video |

レビュー:
`episodes/out14_push_microarc_editorial_v2_20260727/artifacts/clip-out14-push-microarc-editorial-v2-001/review/index.html`

## 実装回帰と最終読戻し

| command / check | actual result |
|---|---|
| `uvx ruff check`（変更したCLI、renderer、test） | all checks passed |
| `uvx --from pytest pytest -q tests/test_push_microarc_editorial_v2.py tests/test_push_microarc_stream.py tests/test_editorial_video_candidate.py` | 76 passed in 17.16s |
| bundled Python `compileall -q src tests` | pass |
| promoted package `_validate_manifest` | closed set pass、29 payload rows + manifest、30 files |
| localhost readback | page 200 / `text/html`、MP4 Range 206 / 1024 bytes / `video/mp4` |
| representative visual inspection | opening、first/middle/last、全cut境界両側、8 selected-range代表、ending、320 thumbnailを確認。破損frame、字幕二重表示、telop/字幕衝突、英単語内分割なし |

このworktreeにはproject dependency manifestがなく、最初の`uv run ruff/pytest`は
program not foundで起動しなかった。test failureではない。tool-isolatedな`uvx`で同じ
対象を再実行し、上記の最終結果を得た。

## 回復過程から残す知見

最初の字幕presentationは一部3行となりfail-closed。word-timed chunkへ直した。
完成レンダー後の検査を一度operator側から停止したため、そのMP4をexact failed artifact identity内で
SHA/size照合し、same-volume hardlinkで検査だけ再開できる回復経路とtestを追加した。
その回復packageは技術greenだったが、実フレームで英単語分割と強すぎる終盤telopを見つけたため採用せず、
原因を修正して全render/validationを再実施した。最終SHAは上記`8fe9105c...53414`だけ。

## 監修判断パケット

監修役はこのSHAを全編確認し、次を一つのreceiptへ記録する。

1. 8 cut / 406.55秒のsetup→escalation→notification→apology→warningが自然か。
2. actual-audio字幕の聞き取り、固有語、false startの扱い、表示時間が妥当か。
3. 4 telopが理解を助け、内容を誇張しないか。
4. title 3案のpromiseとtoneが実内容に一致するか。
5. actual-frame thumbnail roughの焦点と短文が妥当か。

結果は`accept / bounded_repair / reject`。unmentioned dimensionsをaccept扱いにしない。
bounded repairはaffected timestamp/dimensionだけを新SHAへ開く。

## 可能な限り先へ進める条件付き目標

| 段階 | 目的と効果 | 開始条件 | 完了証拠 / owner |
|---|---|---|---|
| G0 | v1 reject/quarantine保存 | 完了 | exact decision JSON / Agent |
| G1 | v2候補・競合selector | 完了 | 3 streams、9 candidates、11 observations、93/100 / Agent |
| G2 | actual-audio字幕・timing | 完了 | 24 anchors、142 cue、非発話0 / Agent |
| G3 | visible structure/title/thumb rough | 完了 | 4 telop、3 title、2 rough / Agent |
| G4 | exact v2 human review | 現在可能 | SHA-bound verdict / Human editorial owner |
| G5 | bounded repair | G4=`bounded_repair` | affected-only new identityと再review / Agent + Human |
| G6 | Factory Contract v2抽出 | G4がacceptまたは修復収束 | candidate card、ASR/align、timeline/telop/thumb policyを再利用可能にする / Supervisor |
| G7 | second real episode repeatability | G6の最小contract | 別episodeで同じ選定・字幕・review gateを通す / Agent |
| G8 | third real episodeとquality trend | G7 pass | 3 episodeの失敗分類、latency、repair率 / Supervisor |
| G9 | rights/material-use判断 | exact accepted artifact、owner、platform、territory | allow/deny/restriction receipt / Rights owner |
| G10 | production subtitle/font | G4 accept、font licenseとdesign owner | device/safe-area/language receipt / Designer |
| G11 | production render/device/audio QC | G9/G10の必要条件 | delivery profile、color/audio/device receipt / Production owner |
| G12 | title/thumbnail/metadata acceptance | final video lock | exact creative receipt / Editorial/marketing owner |
| G13 | private/unlisted delivery | G9–G12、credentials明示承認 | OAuth/idempotency/rollback receipt / Account owner |
| G14 | explicit public release | private delivery確認、全owner承認 | publication/visibility receipt / Human owner |
| G15 | multi-episode operations | 3+ accepted episode、contract安定 | queue/retry/retention/quality/cost observability / Supervisor |
| G16 | policy-constrained autonomy | G15の監査データ | 自動停止条件、budget、quality drift、manual override / Owner |

G4がrejectならG5を飛ばし、理由をG6のcontract設計へ戻す。rights/public gateが閉じたままでも
G6–G8のinternal repeatabilityは進められる。G9以降は技術greenから自動的に開かない。

## 次の取っ掛かり

- **Advance**: exact v2を全編reviewし、G4 receiptを作る。これが最短のbottleneck解消。
- **Audit**: 監修前に142 cueの低confidence箇所だけを抽出し、全編判断の確認点を減らす。
- **Explore**: G6 Factory Contract v2のschema境界だけを設計し、4本目のrenderへ先走らない。
- **Verify**: protected hashes、Git clean、tracked episode 0、local review availabilityを再確認する。

drift観察では、v1への個別美容調整、docsだけの完了扱い、4本目のtopic renderは回避した。
次consumerはG4 human editorial ownerで明確。production/public判断はまだconsumerを移していない。
