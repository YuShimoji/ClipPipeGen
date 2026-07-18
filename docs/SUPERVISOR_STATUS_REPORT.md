# ClipPipeGen 監修役向け現状報告 — 2026-07-18

## 監修上の結論

OUT-09 second-source repeatabilityは、指定base
`29a1a51902bf8140862839e077936b908f775167`から独立branchで実装され、実source取得、
real transcript authority、宣言的plan、1回の実render、media/frame/browser QAまで完了した。
OUT-08のID `7J5aS_pcBj4`とは異なる`D4i4fjs9PWc`から、27.720秒のreviewable
1080x1920 Shortを大規模rewriteなしで生成できたため、cross-source plumbingの最初の
成功例としては十分である。

ただし現在状態は`review_ready`で、`accepted`ではない。監修上の次のボトルネックは
実装や配管ではなく、exact MP4について「1本のShortとして成立するか」「境界・字幕・
音声・映像に違和感があるか」の二点を人間が判断することにある。原動画内captionとの
二重表示と`support`の途中wrapを既知quality debtとして隠さず残したため、先にこの判断を
閉じ、accept / bounded repair / rejectを選ぶべきである。

rights、production render、production subtitle design、thumbnail、public/publishing、
OAuth/upload、portability、H1は閉じたまま。OUT-09成功だけでそれらを前倒ししない。

## 同期・branch・scope

| 確認対象 | 実測 | 監修上の意味 |
|---|---|---|
| base | `29a1a51902bf8140862839e077936b908f775167` | Prompt指定baseと一致 |
| branch | `codex/out-09-second-source-short-repeatability-v0` | mainへmergeせず独立review可能 |
| scope | ClipPipeGenのみ | NLMYTGenを含む他repoは未読・未編集 |
| episode storage | ignored `episodes/holoen01_kronii_wisdomteeth_out09_20260718/` | source/media/private review payloadをGitへ入れない |
| active preview保護 | 既存episode/human previewを削除せず新episodeへ出力 | broad ignored cleanupなし |
| render budget | actual 1、corrective 0 | one-pass/no-micro-tuningを遵守 |

branchのcommit/push/parityはcloseoutで確定する。docsはartifactとbrowser evidenceの確定後に
一度だけ同期した。

## source とtranscriptの選択

既存在庫にはOUT-08と異なる完成済み実episodeがなかった。repo authorityに既知かつ
public、認証不要、過去にpipeline実績のあるOuro Kronii source
`https://www.youtube.com/watch?v=D4i4fjs9PWc`が記録されていたため、既存
`fetch-source-video` / `fetch-source-audio` routeで新episodeへ再取得した。

| evidence | 結果 | 境界 |
|---|---|---|
| source video | `61c06f75...fd938`、640x360、H.264/AAC、77.786848s | 現行yt-dlpのJS runtime/format制約。production画質主張なし |
| source audio | `b33b3521...f81b`、mono PCM 16kHz、77.738688s | STT/render用実audio |
| Vosk EN | real transcript、13 segments | 誤認識が多く表示字幕の正本から除外 |
| English Original JSON3 | `36bdbf38...83e6` | YouTube auto-caption、human acceptanceではない |
| imported transcript | `subtitle_track/youtube_subtitles`、24 segments、24 aligned | rolling overlap 21、review status needs_review |
| edit authority | 3 cuts、context `3 passed` | candidateはcut_002 + cut_003 envelope内 |

Voskを捨てずbase provenanceとしてhash固定しつつ、表示字幕はcaption importへ切り替えた。
display文はrolling captionを短くdedupeし、linked source segment textのtoken subsequenceで
あることをbuilderがrender前に検証する。これにより「real providerである」ことと
「human transcript acceptedである」ことを混同しない。

## 実装した再利用境界

新builderはsource固有ID、時刻、字幕本文をcodeへ埋め込まない。ignored planが次を宣言し、
generic validatorが読む。

- OUT-08と異なるsource identity
- source video/audio material IDsとhash
- rights/ledger/base Vosk/caption/imported transcript/edit packの6 input paths/hashes
- context-passed cut authority、allowed range、excluded/unselected ranges
- source segment linkageとdisplay normalization
- narrative arc、candidate duration、二つのhuman question
- rights/public/production/H1のclosed gates

OUT-05のvertical renderer、OUT-06のmanifest self-integrity、OUT-08のatomic promotion、
navigation/frame QA、ASS/SRT/Range review surfaceを再利用した。source違いに応じて増えた
実装はplan validationとprovenance readbackであり、renderer分岐ではない。

## artifact とvalidation

| 項目 | exact readback |
|---|---|
| artifact | `clip-out09-second-source-short-repeatability-v0-001` |
| package | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/` |
| candidate | source `31.160–58.880s`、semantic `27.720s`、media `27.733333s` |
| video | 5,863,660 bytes、SHA-256 `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9` |
| format | H.264 High / AAC / 1080x1920 / 30fps / yuv420p / faststart |
| subtitles | 7 ASS burn-in events + SRT、containment passed、最大3行 |
| audio | normalized `-14.54 LUFS / -1.48 dBTP` |
| signal QA | blackdetect event 0、silencedetect event 0 |
| decode | full video/audio decode exit 0、stderr empty |
| frame QA | `0.250 / 9.425 / 15.160 / 27.470s` contact sheet |
| manifest | self-integrity `3f55d16388b1b4197d35ad0e4385e711353932366d8f93ff60ee04500deea692` |
| browser | page 200、Range 206、readyState 4、media error null、seek/resume advance、overflow false、console clean |
| elapsed | builder 47.413s、外側48.01s |

review URLは`http://127.0.0.1:8072/index.html`。再起動commandは次である。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

## 現在の判断packet

人間に求める回答は二つだけ。

1. 内容とテンポは、1本のShortとして成立していますか？
2. 境界・字幕・音声・映像に違和感はありますか？

判断対象は上記MP4 hashに限定する。frame QAで次を確認済みで、回答時に隠さない。

- source-native小captionとOUT-09大字幕が同時に見える。
- `out09_sub_006`の`support`が`suppo / rt`へ途中wrapする。
- safe envelope、media decode、overflow、音量、black/silence、browser再生はpassed。
- sourceは640x360からのreframe/upscaleで、production画質acceptanceではない。

回答が「成立し、違和感なし」ならexact candidateをinternal acceptへ遷移できる。字幕の
途中wrapまたは二重表示が違和感なら、同じsource/candidate identityを保つbounded repair
を1回だけ別sliceで定義する。内容やテンポが成立しないなら、format tuneではなくcandidate
selection failureとしてrejectし、failure taxonomyへ残す。

## 残作業の責任と次の動き

| 作業 | 目的 | 効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|---|
| OUT-09 human review | exact候補のcreative/readability判断 | review_readyをaccept/repair/rejectへ変える | localhost再生と二問回答 | pending | Human ownerが二問へ回答 |
| subtitle debt classification | 二重captionと途中wrapをsource固有/共通問題へ分ける | one-off micro-tuneを避ける | OUT-09回答 + 次source観測 | dataあり、未一般化 | Agentがportfolio時に集計、Supervisorがrule昇格判断 |
| source quality/tooling | 640x360取得制約を可視化 | 次sourceのformat選定を安定化 | yt-dlp/JS runtime方針 | diagnostic debt | Tooling ownerがG2前後で必要時だけ扱う |
| rights clearance | material use判断を人間へ渡す | production/public gateの前提 | source identity、guideline/owner判断 | `pending` | Rights owner。OUT-09 reviewと混ぜない |
| artifact portability | 別端末reviewを可能にする | same-machine依存を下げる | retention/private transfer方針 | scope外 | Infra owner。現在のacceptance条件ではない |

true blockerはhuman answerだけ。credentials、public state、rights判断、destructive git操作は
実行していない。

## project全体の現在地

| workflow | 到達済み | 次の本質的gap |
|---|---|---|
| source/material | local/URL acquisition、sidecar、ledger、receipt、hash | source横断format/toolingの安定性 |
| transcript | Vosk JP/EN、subtitle import、review patch、provenance | human correction、speaker、official captionなしsource |
| editing | cut/context/subtitle/NLE/review packet、宣言的range | creative selection failure taxonomy |
| output | OUT-03〜OUT-09、real vertical、decode/audio/frame/browser | 3〜5本でのrepeatabilityとproduction acceptance |
| subtitle | measured wrap、ASS/SRT、source-linked normalization | word boundary、二重caption、production design |
| thumbnail | OUT-07 provisional usable direction | 3〜5本比較後のcanonical/default判断 |
| rights | pending readbackをhard gateにせず保持 | human material-use clearance |
| publishing | integration boundaryのみ | credentials、安全なvisibility、receipt/rollback |
| operator UX | CLI/docs/dashboard/artifact launcher | episode全体を一画面で再開するcockpit |

## 開発を可能な限り先へ進める目標階段

目標は依存順に置く。遠い目標を記録するが、手前のacceptanceを飛ばさない。

| 段階 | 目標 | 完了信号 | 先に必要なもの | 現在状態 |
|---|---|---|---|---|
| G0 | OUT-09 exact human decision | 二問回答をMP4 hashへ結び、accept/repair/rejectを記録 | 現在のreview package | **active / pending** |
| G1 | OUT-09 bounded closure | 必要なら限定repairを一回だけ行い、OUT-09を閉じる | G0回答 | 未着手。不要ならskip |
| G2 | 3〜5本real Shorts portfolio | sourceごとのduration、caption authority、wrap、audio、render/browser、human resultを同じscorecardで比較 | G0/G1 closure、追加source承認 | proposal |
| G3 | cross-source failure taxonomy | selection/transcript/wrap/reframe/toolingを分類し、共通fixとsource例外を分離 | G2の複数結果 | proposal |
| G4 | production limitation-lift packet | production renderとproduction subtitle designを別々にaccept/rejectできるexact evidence | G2/G3、明示的production scope | gate closed |
| G5 | rights/material-use clearance | 一候補の利用条件、制限、判断者、receiptが明確 | exact candidate、rights owner | `pending` |
| G6 | thumbnail system再開 | 3〜5本を比較し、偶然でないcover方向を選ぶ。canonical/defaultは別判断 | G2 portfolio、独立review | OUT-07 parked |
| G7 | private/unlisted delivery | dry-run、safe visibility、upload/thumbnail receipt、rollback付きhandoff | G4〜G6の必要gate、OAuth承認 | 未実装 |
| G8 | episode operator cockpit | source→evidence→decision→deliveryを一画面で追跡し、artifact探索を減らす | 安定したG2〜G7 contract | proposal |
| G9 | multi-episode production-assist loop | 複数episodeでtraceable artifact、human gate、rollback、private/public handoffを再現 | G8、retention/privacy、運用KPI | long-term north star |

G9の最終像は、承認済みsourceを入力し、source/rights/transcript/edit/subtitle/output/
thumbnail/publish metadataを一つのepisode lineageでつなぎ、各human gateを越えたものだけを
private/unlisted/public deliveryへ渡し、全操作をreceiptとrollback情報で再現する
production-assist loopである。公開判断やrights判断そのものは自動化しない。

## 直近の推奨順

1. **Verify** — OUT-09の二問へ回答し、exact identityを閉じる。
2. **Audit** — 回答結果を二重caption/word-boundary/fidelityのtaxonomyへ記録する。
3. **Advance** — 別sourceを増やし、3〜5本portfolioを作る。
4. **Explore** — portfolioからproduction limitation-lift packetを設計する。

今はVerifyが唯一の最短経路。OUT-09判断前にthumbnail、publishing、portability、docs-health、
H1へ横展開すると、配管成功と品質成功が混ざるため進めない。
