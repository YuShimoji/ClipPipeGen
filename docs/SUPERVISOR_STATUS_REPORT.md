# ClipPipeGen 監修役向け現状報告 — 2026-07-18 OUT-09 Bounded Repair

## 監修上の結論

OUT-09初回候補へのユーザーfeedbackは、内容選択のreject/acceptではなく、追加字幕の
presentation/timingと終端editだけに対する`bounded_repair_required`だった。この二点を
同じsource、主題、開始点、artifact ID、candidate IDのまま、corrective render 1回で
修復した。

状態は
`OUT09_DISTINCT_REAL_SOURCE_SHORT_REPEATABILITY_REVIEW_READY`から
`OUT09_SUBTITLE_AUTHORITY_AND_ENDPOINT_REPAIRED_REVIEW_READY`へ遷移した。これは
acceptance closureでもproduction reframeでもない。新MP4 SHAだけが次の人間判断対象で、
human acceptanceはpendingである。

## User feedbackの記録

| 軸 | 記録値 | 今回の扱い |
|---|---|---|
| overall | `bounded_repair_required` | 同一candidateの限定修復 |
| content selection | `not_rejected_not_yet_accepted` | 開始・主題・中心構成を維持 |
| subtitle presentation/timing | `needs_adjustment` | native-caption-onlyへ変更 |
| endpoint edit | `needs_adjustment` | 実caption/audio/scene根拠で延長 |

## Subtitle authorityのbefore/after

sourceには短周期で切り替わるburned-in English captionがある。初回はその上に
ClipPipeGenの長文ASSを追加burn-inしたため、二重字幕、切替timing衝突、`support`の
途中wrapが見えた。

| 項目 | Before | After |
|---|---|---|
| on-screen authority | native caption + ClipPipeGen長文ASS | `source_native_caption_pixels`のみ |
| additional burn-in | 7 visible events | 0 visible events / `burn_in_applied=false` |
| ASS/SRT | 表示とprovenanceを兼用 | 9eventをprovenance/navigation/machine readback sidecar-onlyで保持 |
| native pixels | reframe後に長文字幕を重ねた | mask/overwrite/changeなし |
| fallback | 未定義 | 判読不能なら`REFRAME_REQUIRED_NATIVE_CAPTION_NOT_LEGIBLE`で停止 |

共有OUT-05 render pathには、Dialogue 0件のinternal ASS carrierを渡す。packageのASS/SRT
は実transcript linkageを維持するが、動画には焼かない。1080x1920 frame、216x384 frame、
375px browser viewportでnative captionを実観測し、mobile video幅341.8pxでも判読できた。

## Endpointのbefore/after

初回end `58.880s`はnative captionが`Man,`、発話も続きの途中だった。source video、
caption JSON3、import transcript、audio silenceを突き合わせ、次を確定した。

| evidence | source time |
|---|---:|
| last native caption completion | `64.360s` |
| last speech completion | `64.362812s` |
| short silence end / next speech | `64.541125s` |
| next scene and next native caption start | `64.480s` |
| selected end-exclusive boundary | `64.480s` |

開始`31.160s`は維持し、次sceneへ入る直前をendにした。固定padding、fade、SFX、
freeze frame、追加無音は使っていない。semantic durationは`27.720→33.320s`、mediaは
`27.733333→33.333333s`になった。

## Exact identityとpackage

| 項目 | 値 |
|---|---|
| artifact / candidate | `clip-out09-second-source-short-repeatability-v0-001` / `candidate_01` |
| source | YouTube `D4i4fjs9PWc`、video `61c06f75...fd938`、audio `b33b3521...f81b` |
| superseded MP4 | `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9`、acceptanceなし |
| repaired MP4 | `3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916`、6,637,874 bytes |
| plan input | `e9e68b1a9dcd1b1edc0691a5cb43675235aa54f4d1a37ddf36b96a7d93fc53c1` |
| manifest self-integrity | `440c73dde6b33e9ba9ce63a512e61f5974e947032a507ac17c560d560a028078` |
| package | `episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/` |

## Renderとvalidation

| 検証 | 結果 |
|---|---|
| corrective render | 1回、追加autonomous repair 0 |
| elapsed | builder `31.729s`、外側`32.276s` |
| targeted tests | OUT-09・直接影響・現状面は`41 passed, 2 skipped, 1 deselected` |
| Ruff | changed scope passed |
| media | H.264 High/AAC、1080x1920、30fps、yuv420p、33.333333s、faststart |
| decode/audio | full decode exit 0、`-14.80 LUFS / -1.46 dBTP` |
| signal | blackdetect 0、silencedetect 0 |
| frames | start、authority boundary、native-caption switch、endpoint caption、endの5点 |
| integrity | 10 package files、6 inputs、plan/readback/manifest/hash/self-integrity一致 |
| HTTP | index 200、MP4 Range 206 / 1024 bytes |
| browser | readyState 4、error null、Space play/pause、ArrowRight seek、resume前進 |
| responsive | desktop/mobile overflow false、question 1件、console warning/error 0 |

## Review entrypoint

URLは`http://127.0.0.1:8072/index.html`。

```powershell
powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072
```

最終質問は一つだけである。

> 字幕の切替リズムと終わり方が自然になったか、ほかに明確な違和感があれば教えてください。

## Evidence boundaryと残るdebt

- verified: source/hash/provenance、plan/readback/manifest、tests、ffprobe/decode、HTTP/Range。
- observed: endpoint前後frame/audio、desktop/mobile caption legibility、browser playback/seek。
- unknown: 修復後exact MP4への人間editorial acceptance。
- closed: rights、production render、production subtitle design、thumbnail、public/publishing、upload/OAuth。
- local-only: ignored packageはThank端末のsame-machine evidence。portabilityは未証明。

技術的に修復したのは二重字幕、途中wrap、長文cue衝突、途中終端。残るquality debtは、
sourceが640x360取得物であること、native captionの読みやすさがこのsource固有観測であること、
human acceptanceがpendingであること。人間回答がcaption判読不能を示した場合だけ
`REFRAME_REQUIRED_NATIVE_CAPTION_NOT_LEGIBLE`、自然終端がなお成立しない場合だけ
`REFRAME_REQUIRED_NO_BOUNDED_ENDPOINT`として同一candidateの追加micro-tuneを止める。

限定テストでは、今回未変更の
`tests/test_vertical_short_candidate.py::test_out06_reviewed_japanese_break_hints_are_measured_and_semantic`
が単独でもfailした。期待3行に対して現行測定が2行を返すOUT-06経路の既知監査事項で、
OUT-09実装ファイルには差分がない。今回のrepairからは1件を明示deselectし、OUT-06の別
regression auditへ所有を分けた。これはOUT-09の人間reviewを止めないが、全repo greenは
主張しない。

## 開発を先へ進める目標階段

| 段階 | 目標 | 完了信号 | 現在状態 |
|---|---|---|---|
| G0 | repaired OUT-09 exact decision | 一問回答を新SHAへ結びaccept / reframe / reject | **active / pending** |
| G1 | OUT-09 closure | 必要ならreframeへ別ID/別sliceで移行し、bounded repairを再反復しない | G0待ち |
| G2 | 3〜5本real Shorts portfolio | source、caption authority、endpoint、human resultを同じscorecardで比較 | proposal |
| G3 | cross-source failure taxonomy | subtitle authority、selection、endpoint、reframe、toolingを共通/固有へ分離 | G2後 |
| G4 | production limitation-lift packet | render acceptanceとsubtitle design acceptanceを別判断可能にする | gate closed |
| G5 | rights/material-use clearance | exact candidateの利用条件と判断receiptを残す | rights owner待ち |
| G6 | thumbnail system再開 | 3〜5本比較後にOUT-07 parked directionを再評価 | G2後 |
| G7 | private/unlisted delivery | visibility、upload receipt、rollbackを伴う安全なhandoff | G4–G6とOAuth承認後 |
| G8 | episode operator cockpit | source→evidence→decision→deliveryを一画面で追跡 | proposal |
| G9 | multi-episode production-assist loop | human gate、lineage、receipt、rollbackを複数episodeで再現 | long-term north star |

H1へ渡せるdataはbefore/after SHA、caption mode、endpoint timing、source resolution、
render elapsed、desktop/mobile/browser readiness、human acceptance pendingのみ。H1を今回
実行したり、native-caption-onlyをproduction policyへ一般化したりしない。
