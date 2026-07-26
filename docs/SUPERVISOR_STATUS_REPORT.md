# OUT-14 Editorial Presentation Reconstruction v3・監修引継ぎ報告

更新日: 2026-07-27 JST

Scope: ClipPipeGen only

mission: `CPG-OUT14-EDITORIAL-PRESENTATION-RECONSTRUCTION-V3`
attempt: `1`

## 現在の結論

`clip-out14-push-microarc-editorial-v3-001`は
`OUT14_EDITORIAL_V3_READY_FOR_HUMAN_REVIEW`。

exact final MP4 SHAは
`fddae5a6688671ad301b1c1dcecd978a50865dd1fb5d678a6d55db1f3c18e9be`、
406.55秒、1920×1080、H.264 Main / AAC。exact manifest file SHAは
`99bb99349b7896a4667358fd14f9c08557d356971823f07a254f2fd35bbace72`。

v2で成立していたepisode、selected source、8 cut、working title、知覚同期を保護し、
viewer-facingでrejectされたthumbnail、日本語分節、引用人物、笑い、cut grammar、
explanation treatmentを新しいv3へ再構成した。full render後に一度全編再生し、
全ledger監査で同型の分節欠陥を追加検出したため、42内部境界を原因層で修復して
再probe・再render・再decode・再全編再生まで完了した。

machine evidenceが証明するのはconstruction、traceability、media integrity、
bounded timing、viewer-facing完走だけ。human editorial acceptance、rights、YPP、
production、thumbnail acceptance、publication、upload、visibilityは閉じたまま。

## repository、remote、preservation

| 対象 | live確認と操作 | 終了状態 |
|---|---|---|
| repository | `YuShimoji/ClipPipeGen`のisolated worktree | 他repoを読書きしていない |
| exact start | `fab5d5a3369fe4d5defab265fa715201c3f8b0cf` | mission指定と一致 |
| `origin/main` | fetch後 `edb782acd1e06aca46e0a5d10295ea52f30ad5c7` | merge / rebaseなし |
| branch | `codex/out14-editorial-presentation-v3` | 新branch再作成なし |
| worktree | `ClipPipeGen-out14-editorial-presentation-v3` | 既存mission worktreeを継続 |
| external effect | push / PR / merge / tag / deploy / upload / publication | 0 |
| private media | `episodes/out14_push_microarc_editorial_v3_20260727/` | ignored、tracked 0 |
| temporary work | probe/master/audio/旧V3候補 | 正式package確定後に削除 |

exact v2はread-onlyで使用した。

| protected v2 identity | 開始／終了照合 |
|---|---|
| artifact | `clip-out14-push-microarc-editorial-v2-001` |
| final MP4 | `8fe9105c72645acbb21357f10107e0266e19d1bebe18c30a68bd7e59b5853414` |
| manifest | `774351a7fc55839e05e58276280570a27ac1fd0aa7fa78283cdcf79f5d8634a9` |
| rejected thumbnail | `d0edde1236f8b254c1fe9588d1f656aef057f1baba603be55239d20c3170c3ce` |
| selected source | `335e9a131fae06b716bd7ac479e914fb849be117b15c4b412c9b4c565fef264e` |
| complete artifact inventory | 30 files、attempt-start/end path-size-hash snapshot一致 |

v1/v2 artifact、source、manifest、review page、decision recordへのwriteは0。
元worktree、origin/main、他branch、user workをstash/reset/restoreしていない。

## human decisionとACTIVE quarantine

v2 verdictはexact MP4とrejected thumbnailへ束縛した。
accepted dimensionは`subtitle_perceptual_timing_improvement_only`。
line break、editorial hierarchy、quote treatment、laughter、transition、
explanation、thumbnailは`BLOCK_CURRENT`。working title、episode selection、rights、
YPP、publication、未指摘箇所をaccepted扱いしていない。

| quarantine | v2 signature | v3でmaterially異なる点 |
|---|---|---|
| `out14-v2-source-screenshot-single-hook-thumbnail-v1` | raw SS、英文面、single consequence、全幅暗色帯 | source crop＋subject separation＋setup/consequence二意味単位 |
| `out14-v2-flat-caption-pass-through-v1` | uniform speech、mechanical split、quote同型、laughter空白 | 5 role hierarchy、42境界統合、quote 100%、laughter 5件 |
| `out14-v2-naked-cut-black-card-v1` | naked jump、full-black explanation | 8 boundary原因分類、material bridge 2、source-anchored panel |

これらはv2 exact identityに対してACTIVEのまま。v3を技術greenにしたことは、
quarantineの解除やv2 acceptedへの書換えではない。

## 生成前actual-surface観測

最初のdirection-generating mutationは
`docs/research/OUT14_EDITORIAL_V3_DESIGN_BASIS.md`。
signatureは`CPG-OUT14-V3-DIRSIG-20260727-A`。

mission専用のfresh temporary user-data-dirをIncognitoで起動し、extensions、
sync、cacheを無効化、全件signed-outで観測した。通常のDefault profile、
保存cookie、Google/YouTube login、履歴、Home、おすすめ、既存拡張を使っていない。

| 観測範囲 | 数 | actual surface |
|---|---:|---|
| channels | 4 | 複数channelを横断し一つをcanonical化しない |
| videos | 9 | 320×180 thumbnail＋actual decoded timestamps |
| same/adjacent premise | 1以上 | Discord全体通知の公開例を含む |
| multi-person / quote | 2以上 | identity cue、speech balloon、speaker colorの構造だけ観測 |
| laughter | 2以上 | `(笑)`相当ではなく`w/ｗｗｗ`等のrole変化を観測 |
| transition/explanation | 2以上 | semantic cut、result graphic、section changeを観測 |

URL、channel、title、checked_at、timestamp、viewport/zoom、profile mode、
account state、surface、限界を記録した。競合画像、映像、音声、字幕、title copy、
layoutは保存、download、複製、近似模倣していない。

Mission Chromeだけを終了し、mission temp profileも削除した。
起動前から存在した13件のChrome processは終了も変更もしていない。
既存profile、OS/既定ブラウザー設定にも触れていない。

## predeclared directionと実装

生成前に次を固定した。

1. thumbnailはsetup「遊びのプロフィール変更」とconsequence「全スタッフへ到達」を
   単独で伝える。reaction-ledはrunner-up。
2. viewer textをnormal speech、quoted speech、laughter/reaction、
   punchline、creator explanationへ分離する。
3. narrating Subaruとquoted identityを混同せず、paraphraseを本人live speechにしない。
4. 全8 boundaryを原因分類し、2:48 / 6:27を無標識のまま残さない。
5. v2 timingをbaselineにし、layout-only cueの時刻を変えない。
6. review順をthumbnail decision sizes→full video→changed probesにする。

実装は次の3 tracked pathへ閉じた。

- `src/integrations/render/push_microarc_editorial_v3.py`
- `src/cli/build_push_microarc_editorial_v3.py`
- `tests/test_push_microarc_editorial_v3.py`

exact v2/source/design signature preflight、staging build、fail-closed pending state、
full-view finalizeを一つのmission-local pathへ接続した。generic editing framework、
Factory Contract一般化、新episode探索には広げていない。

## thumbnail再構成

notification reveal、strong reaction、apology、ending warningの4時点からcontact sheetを作成。
各source timestamp、frame SHA、crop、用途をledgerへ保存した。

selectedはnotification reveal frameを背景に、左のcreator panelと
`遊びでプロフィール変更 / 全スタッフに / 届いてた`を主従2階層で構成した。
raw screenshot全面構成、全幅半透明黒帯、外部portrait、AI生成画像は使っていない。

| output | SHA-256 | self-review |
|---|---|---|
| selected 1280×720 | `e6e6bbca25319108ae5f4c356953c2d1fa1814937ebeb90a138b1f03e7133988` | zoom確認用 |
| selected 320×180 | `80a9847fc3377f722ff87e3071fe35754c7806d4f372941b6d7e77ebc52d6f59` | setup/consequence保持 |
| selected 160×90 | `167917be436092f29ad8fcd2ba15b4acaad6d9e7875b8291d6a0910296090528` | subject/text保持 |
| runner-up 320×180 | `6ea5fa71fbb60bf45b73983edb03cdae05de2c4dcaf06718bdf669525d73a708` | reaction-led比較 |

duration badge simulationのcritical overlapは0。
external/generated assetは0。titleを隠してもpremiseを概ね説明でき、
titleと同じ文章を機械反復していない。publication thumbnail acceptanceは未判定。

## 日本語分節の原因層修復

最初の実装は0:15の`なん / か最近`を12.64→12.72秒へ修復したが、
初回full playback後の全142 cue ledger監査で
`レッドカ / ード`、`メンバ / ー`、`恐れない / でください`、
`いき / なり`、`す / いません`等の同型境界を追加検出した。

既知locusだけのliteral replacementを止め、31 phrase groupで42内部境界を統合し、
未完の1文字fragment 1件をviewer-facingから抑制した。canonical text/orderと
group外側のword-timed intervalはtraceableなまま。quote eventは統合対象外。

| QA | 結果 |
|---|---:|
| canonical / viewer cues | 142 / 99 |
| within-word split | 0 |
| isolated single character | 0 |
| dangling particle / auxiliary / short predicate | 0 |
| kinsoku line-break violation | 0 |
| 3-line / overdense | 0 / 0 |
| changed timing median / p95 absolute | 80ms / 80ms |
| systematic late bias | false |

実rasterで0:15と追加6時点をcontact sheet化し、全件2行以内、
重大なface/source-UI collisionなしを目視した。

## speaker、quote、laughter

narrating speakerは全件`大空スバル`。verified quoteは次の5 event。

| event | quoted identity | evidence | treatment |
|---|---|---|---|
| `speech_0018` | 猫又おかゆ | 直前attribution＋canonical quote | name cue＋purple quote |
| `speech_0100/0101` | 星街すいせい | `すいちゃんから`直後の連続quote | name cue＋blue accent |
| `speech_0107` | さくらみこ | `みこち`直後のcanonical quote | name cue＋pink accent |
| `speech_0113` | 星街すいせい | `すいちゃん`直後のquote | same verified role |

distinct treatment coverage 1.0、identity不明をverbatim装飾した件数0、
external portrait 0。paraphraseはnormal speechに残した。

actual viewer-facing audio 406.55秒とbounded windowsを監査した。

| intensity | events | marker | motion |
|---|---|---|---|
| mild | 2 | `(笑)` | none |
| strong / sustained | 3 | `ｗｗｗ` | deterministic 1–4px |

strong seedsは`21455 / 30620 / 37890`。unhandled required 0、
provider annotation leak 0、全画面jitter・通常字幕jitter・非決定randomは0。

## cut、explanation、audio

全8 cut startにsource ranges、v2/v3 output、audio/visual state、decision、理由、
前後5秒のinspection windowを保存した。

| output | classification | treatment |
|---:|---|---|
| 0.00 | sequence start | premise tag |
| 50.28 | same-scene omission | 40ms microfade＋context accent |
| 115.16 | semantic beat | 40ms microfade＋work tag |
| 167.72 | time jump | 40ms microfade＋cyan directional bridge |
| 244.00 | semantic beat | 40ms microfade＋notification reveal |
| 336.08 | semantic beat | 40ms microfade＋apology tag |
| 366.68 | same-scene omission | 40ms microfade＋aftermath marker |
| 386.44 | explanation/ending | 40ms microfade＋source-anchored panel |

全cutへ同じvisual fadeを適用していない。2:48と6:27のactual probeはdecode pass。
6:27後はsource footageを視覚錨に
`注意｜プロフィール変更は全体通知 / 設定変更の通知先を確認`をcompact表示し、
full black＋white text signatureを消した。

全cut black 0。0.5秒freeze 1件は383.967–384.467秒のsource holdで、
386.44秒のjoin前。修復前後のAAC stream SHAは
`fe046c95d81b5e3b1a6488c954f50d2197eae7072acc31b072f754ffa0baee79`
で一致した。したがってsample-level join auditの最大0.07254
（threshold 0.08）をfinalへ束縛できる。

## probe、full render、self-review

probe r1は6:27 explanationにliteral escapeが出る問題と、
2:48 bridgeが弱い問題を検出し、r2で修復。

初回formal renderと406.55秒full playback後、全ledgerとの照合で同型分節残存を発見。
r3でfull-ledger groupingを実装し、r4で
`恐れないでください / いきなり / いってんの`をline-wrap protected phraseへ追加。
追加6時点contact sheetを目視してからformal rerenderした。

final review pageで0→406.55秒を速度1.0、volume 1、mute falseで再生。
8 checkpointsすべて`readyState:4`、stallなし、終端`ended:true`。
opening、quote、mild/strong laughter、全cut、2:48、6:27、explanation、payoff、
endingはcontinuous playbackとrepresentative probeの組合せで確認した。

## 最終mediaと検証

| 検証 | actual result |
|---|---|
| final media | H.264 Main / AAC LC、1920×1080/60、406.55秒 |
| video/audio start | 0 / 0 |
| video/audio duration | 406.550 / 406.545秒 |
| full decode | pass、stderr error 0 |
| faststart | `moov` offset 36 < `mdat` offset 650491 |
| loudness / peak | -14.9 LUFS / -1.7 dBFS |
| silence / black | 0 / 0 |
| probe decode | 9 / 9 pass |
| manifest | 47 payload、closed-set pass |
| full viewer playback | 406.55秒、8 checkpoints、ended true |

focused/nearest regression:

| command | result |
|---|---|
| `pytest tests/test_push_microarc_editorial_v3.py tests/test_push_microarc_editorial_v2.py -q` | 21 passed |
| `pytest -q` with the repository-required Pillow dependency | 706 passed |
| `ruff check` on V3 renderer/CLI/test | all checks passed |
| bundled Python `compileall -q` on V3 renderer/CLI/test | pass |
| `git diff --check` | pass |
| changed-diff private path/secret/token scan | secret 0。boundary記述のcookie文字だけ |
| `git ls-files episodes` | 0 |
| changed media extension scan | 0 |

bare `uv run --with pytest`は既知のPillow未注入で2 moduleのcollection停止となるため、
既存repository contractどおり`--with pillow`を追加して全706件を完走した。
旧OUT-14 authorityを固定していた8 assertionは、v3のRuntime/Handoff/artifact registryと
一致するよう更新し、current authorityの不一致を検出するnegative testは維持した。

## 監修判断パケット

次のhuman reviewはexact v3全体について、残る重大問題の有無を判断する。
全字幕の再校正や全cutのチェックリスト入力は不要。

1. 6分46秒の因果、間、role hierarchyが一話として自然か。
2. 99 viewer-facing cueの言語精度と読みやすさに重大問題が残るか。
3. quote/laughter/transition/explanationが理解を助け、過剰演出になっていないか。
4. selected thumbnailがtitleなしでもsetup＋consequenceを伝えるか。
5. working titleのpromiseと最終video/thumbnailが一致するか。

結果は`accept / bounded_repair / reject`の一つをexact SHAへ束縛する。
`accept`はinternal editorial scopeだけ。`bounded_repair`は影響dimension/timestampだけを
新SHAへ開く。`reject`はv3 candidateを閉じる。いずれもrights/public gateを開かない。

## 条件付き長期目標

技術greenから自動で先の権限へ進まず、各gateのownerとreceiptを明示する。

| 段階 | 目的と可能になること | 開始条件 | 完了証拠 / owner |
|---|---|---|---|
| G0 | v2 decision/quarantine保存 | 完了 | exact v2 locator / Agent |
| G1 | v3 presentation reconstruction | 完了 | exact v3 package / Agent |
| G2 | exact v3 overall review | 現在可能 | SHA-bound verdict / Human editorial owner |
| G3 | affected-only repair | G2=`bounded_repair` | new SHA＋affected probes＋re-review / Agent＋Human |
| G4 | internal editorial lock | G2 acceptまたはG3収束 | accepted dimensions receipt / Human |
| G5 | mission-specific contract抽出 | G4 | selector以外のpresentation stop条件を文書化 / Supervisor |
| G6 | second accepted episode repeat | G5最小contract | 別episodeで同gate通過 / Agent |
| G7 | third accepted episode trend | G6 | 3 episodeのrepair率・失敗分類・latency / Supervisor |
| G8 | rights/material-use decision | exact accepted media、platform、territory | allow/deny/restriction receipt / Rights owner |
| G9 | production subtitle/font lock | G4＋font/license/design owner | safe-area/device/language receipt / Designer |
| G10 | production render/audio/device QC | G8/G9の必要条件 | delivery profileとQC receipt / Production owner |
| G11 | title/thumbnail/metadata acceptance | final video lock | exact creative receipt / Editorial/marketing |
| G12 | private/unlisted delivery rehearsal | G8–G11＋credential authority | idempotency/rollback receipt / Account owner |
| G13 | explicit private delivery | G12 pass＋明示承認 | remote object identity / Account owner |
| G14 | explicit public release | private確認＋全owner承認 | publication/visibility receipt / Human owner |
| G15 | multi-episode operations | 3+ accepted episode＋contract安定 | queue/retry/retention/quality/cost telemetry |
| G16 | policy-constrained autonomy | G15監査データ | stop条件、budget、quality drift、manual override |

G2がrejectならG3を飛ばし、理由をG5のstop条件へ戻す。
rights/public gateが閉じたままでもG5–G7のinternal repeatabilityは可能。
G8以降は別ownerの明示receiptなしに開始しない。

## 次の取っ掛かり

- **Advance**: exact v3を全編reviewしG2 verdictを束縛する。現在の唯一の主要bottleneck。
- **Audit**: 監修役が指摘した重大箇所だけをtimestamp付きで絞り、G3の影響範囲を閉じる。
- **Explore**: G4後に限り、今回のpresentation stop条件をmission-specific contractへ抽出する。
- **Verify**: review前にfinal SHA、manifest SHA、localhost Range、protected v2 hashを再読戻しする。

drift監査では、新episode探索、Factory Contract一般化、競合style模倣、
production/public作業への先走りは発生していない。次consumerはhuman editorial ownerで明確。

## 非blockerの既存文書debt

dashboard v1.5の再生成は成功しcurrent v3を向いたが、既存wiki全体には
`stale / over_guarded / unclear`分類の30 findingが残る。これはexact v3の
再生・判断を妨げず、今回のartifactへ便乗して広範囲に直さない。

| 残作業 | 目的と効果 | 必要条件 | 状態 / owner | 次の動き |
|---|---|---|---|---|
| 長大な`docs/HANDOFF.md`の縮約 | current authorityとの競合を減らす | v3 human verdict後も履歴locatorを失わない移送計画 | nonblocking / Documentation owner | 短いpointer化とhistory archiveを別sliceで行う |
| Artifact Registryのv1.5 front sections | current / next / constraintsを先頭で読めるようにする | 既存85 entryを壊さないgenerator test | nonblocking / Documentation owner | `What This Is / Current State / Next / Constraints`を追加 |
| Feature Registryの可読性 | 120 featureの探索摩擦を下げる | authority rowを複製しない生成方式 | long-range / Tooling owner | feature page生成をproposalとして検証 |
