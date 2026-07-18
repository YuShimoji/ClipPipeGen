# 監修AI向け現状報告 — OUT-09 caption presentation repair

更新日: 2026-07-18

対象: ClipPipeGen / `codex/out-09-second-source-short-repeatability-v0`

状態: `OUT09_CLEAR_SHORT_CUE_CAPTION_PRESENTATION_REVIEW_READY`

## 結論

OUT-09は、同一candidateのcaption presentation欠陥を補正render 1回で修復し、技術的な
review-readyへ戻った。current MP4は
`b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50`。
human acceptanceはpendingであり、監修側が次に要求すべき判断は、下記の一問に対する
人間回答だけである。

> 字幕が短い単位で自然に切り替わり、画面を邪魔せず読めるか。最後の終わり方を含め、ほかに明確な違和感があれば教えてください。

content selectionはrejectされていないがacceptもされていない。source range、endpoint、
rights、production、thumbnail、public/publishingを同時に再審議してはならない。

## 人間観測が覆した前提

前版`3e7ef9d8...2916`に対する人間の実見は、次の3点を確定した。

1. source-native captionは中央の16:9 foreground内では縦型review sizeに対して小さすぎる。
2. full-source blurはsource-native caption字形を下部canvasへ複製する。
3. 下部canvasは霜ガラス状に見え、読みやすい字幕面になっていない。

この観測は従前のAgent/machineによる「native captionはmobileでも判読可能」という評価より
上位のauthorityである。したがって、前版のmedia/HTTP/browser successは再生可能性の証拠
としては残るが、字幕presentation acceptanceの証拠としては失効した。

## 世代比較とrepair lineage

| 世代 | semantic範囲 | 表示字幕 | canvas | exact MP4 | 現在の扱い |
|---|---|---|---|---|---|
| initial | `31.160–58.880s` / 27.720s | native + 長文burn-in | full-source blur | `300ee360e0b14c04345dec8df0d6ffd6b2eba85e655624ef7eb338426679e0c9` | superseded、acceptanceなし |
| failed repair | `31.160–64.480s` / 33.320s | 小さいnativeのみ | caption字形を含むfull-source blur | `3e7ef9d883cd10660b6aa95bdf9af364e076c3594b27c73c7ad065ad85a92916` | 人間観測でpresentation失敗 |
| current | `31.160–64.480s` / 33.320s | JSON3由来27 short cues | caption-free cropのみ | `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50` | human review pending |

readback/manifestのrepair lineageはindex 2で、initialとfailed repairの双方、失敗理由
`unreadable_native_caption_and_blurred_caption_duplication`、人間観測を保持する。
predecessor acceptanceをcurrentへ継承していない。

## 今回の補正設計

### Caption-free構図

sourceは`640x360`。caption-activeな10 frame
`31.41 / 34.56 / 37.76 / 41.02 / 45.24 / 49.36 / 53.24 / 57.52 / 61.20 / 64.10s`
を測定し、native caption bandを`x=0,y=286,w=640,h=74`とした。

| 用途 | pixel rectangle | normalized | 制約 |
|---|---|---|---|
| foreground | `0,0,640,286` | `0,0,1,0.7944444444` | native caption bandを含めない |
| background source | `0,0,640,286` | `0,0,1,0.7944444444` | このcropだけをscale/blurする |
| excluded caption band | `0,286,640,74` | `0,0.7944444444,1,0.2055555556` | foreground/backgroundの双方から除外 |

10 frameで顔、人物、主動作、会話contextが保持され、crop conflictは`none`、maskは不使用。
full-source blur fallbackはfalse。fallbackを要する場合もneutral solidまたはcaption-free edge
だけを許す。opaque matteはcropが重要内容と衝突する場合の次候補だが、今回は不要だった。

### Short-cue表示authority

表示authorityは`generated_short_cue_overlay_from_source_json3`。YouTube JSON3のevent開始と
token offsetをsource timing authorityとし、ASS/SRTの27 Dialogue/cueをそのまま動画へ
burn-inした。source-native caption pixelsはbottom cropで抑止している。

| 指標 | 実測 |
|---|---:|
| cue数 | 27 |
| 単語数 | min 1 / max 6 |
| 行数 | min 1 / max 2 |
| cue長 | min 0.48s / max 2.36s |
| 2行cue | 2 |
| whole-word wrap | true |
| last cue | `So.`、sequence `30.840–33.200s` |

字幕plateはopaque solid black、明瞭なoutline/shadowを使う。blur、半透明mask、frosted
glassをsubtitle surfaceとして使わない。ASS/SRTはdisplayとprovenanceの双方を担い、
`burn_in_applied=true`、`visible_overlay_event_count=27`で一致する。

### 変更していないendpoint

source end `64.480s`は前回のendpoint repairで確定した値で、今回reopenしていない。
last native caption `64.360s`、last speech `64.362812s`の後、next scene/caption
`64.480s`の直前でend-exclusiveに閉じる。固定padding、fade、SFX、freeze、追加無音はない。

## 成果物とmachine readback

artifact IDは`clip-out09-second-source-short-repeatability-v0-001`。ignored同一マシンpackage:

`episodes/holoen01_kronii_wisdomteeth_out09_20260718/review/out09_second_source_short_repeatability/`

| 証跡 | 値 |
|---|---|
| candidate MP4 | 5,976,722 bytes / SHA `b6b90a4b29cdc61eb70b6f0f6476fffa8a5d0b148d9ed85a66a36ab8fa73da50` |
| media | H.264 High + AAC LC、1080x1920、30fps、yuv420p、33.333008s |
| plan input | SHA `569ba9d193348d76ee368dde32ebd7c00c485a03792b4728562efec452b00c7e` |
| manifest self | `fec262226982bab5f650b954efb121f646d19d054896cf93a0e1098ccaba1aa7` |
| package integrity | 10 package files / 6 authority inputs一致、plan snapshot一致 |
| frame QA | 10-point contact SHA `792f6b2f7cb5dae54fe8e0eb3fd33298008b7ce99d057b947ffdf7d6be799901` |
| navigation frame | SHA `1df89d1f9c77151ad6a8992418380a89f73c714cc7c67868f608a9631618156d`、review navigation-only |
| ASS/SRT | 27 events / 27 cues |
| render budget | corrective 1回、追加0、builder 32.904s、外側33.498s |

入力のsource video/audio、rights manifest、material ledger、base Vosk transcript、English
Original JSON3、imported authoritative transcript、edit packのhashは従前authorityと一致し、
source/title/episodeの協調置換はない。

## 実媒体・frame・browser検証

| 面 | 結果 | 証拠境界 |
|---|---|---|
| decode | video/audio mapを最後までdecode、exit 0、stderr empty | fileが技術的にdecode可能 |
| faststart | `moov` before `mdat` | local/browser review向けcontainer |
| loudness | input `-27.77 LUFS / -6.87 dBTP`、output `-14.80 LUFS / -1.46 dBTP` | internal targetへのnormalize。production mix acceptanceではない |
| signal | blackdetect 0、silencedetect 0 | 長い黒/無音のobjective failureなし |
| 10 frame contact | native caption、blurred glyph duplicate、frosted surfaceなし。短cue、顔、主動作、final `So.`を確認 | sampled visual evidence。全frame OCRではない |
| HTTP | root 200、MP4 Range 206 | local review delivery path |
| browser media | readyState 4、error null、duration 33.333008、1080x1920 | Chromium系in-app browserでのreadback |
| interaction | native controlへfocus後、Spaceでplay、再Spaceでpause。currentTime前進 | playback viability。全端末操作保証ではない |
| layout | default幅と375px級でhorizontal overflow false | tested viewportだけ |
| review surface | question exactly 1、old questionなし、cache-busted MP4/poster URL | current SHAへのreview誘導 |
| console | warn/error 0 | このlocal page load中のみ |

preview URLは`http://127.0.0.1:8072/index.html`。再起動commandは
`powershell -ExecutionPolicy Bypass -File episodes\holoen01_kronii_wisdomteeth_out09_20260718\review\out09_second_source_short_repeatability\open_preview.ps1 -Port 8072`。

## Codeと限定回帰

shared vertical rendererへ任意`composition_policy`を追加した。未指定時は従来の
full-source background/foreground filterを維持し、OUT-09だけがcaption-free cropを渡す。
policy validationはsource dimension、crop、caption band非交差、bottom-crop整合、
full-source fallback/frosted surface禁止をfail-closedで確認する。

| 実行 | 結果 |
|---|---|
| Ruff: renderer 2 files + OUT-09 test | passed |
| `tests/test_second_source_short_repeatability.py` | 13 passed |
| shared consumers: vertical / complete narrative / real unused range | 33 passed / 2 deselected |
| full repository pytest | 未実行。contractのvalidation budget外 |
| GUI / Electron | 未実行。contractで禁止 |

2 deselectedは既存OUT-06 reviewed-wrap expectations:

- `test_out06_reviewed_japanese_break_hints_are_measured_and_semantic`
- `test_out06_reviewed_wraps_are_repaired_in_package_readback`

これは今回のcaption-free composition/OUT-09 short-cue経路とは別の既存監査事項であり、
このslice内でshared behaviorを変えて解消していない。full-greenは主張しない。

## Git・保存境界

- branch: `codex/out-09-second-source-short-repeatability-v0`
- input base / repair predecessor tip: `754a15856b4d397b89b560f4a73535fddd8f496c`
- tracked implementation/docs/testsは同一branchへcommit/pushする。
- `episodes/`はignoredを維持し、`git ls-files episodes`は0。current packageは同一マシン
  evidenceで、別cloneから自動取得できるportable artifactではない。
- OUT-08以前、protected preview、他repositoryは変更していない。

## 未確定事項とowner

| 残件 | 効果 | 必要条件 | 現在状態 | owner / 次の動き |
|---|---|---|---|---|
| current SHAの見た目 | OUT-09 accept/reframe/rejectを確定 | 人間が一問へ回答 | pending | user。回答をexact SHAへbind |
| OUT-06 wrap test debt | shared reviewed-wrap期待値のgreen化 | OUT-06専用再現と期待値/実装authority確認 | 2 tests deselected | future OUT-06 audit。OUT-09と混ぜない |
| transcript品質 | cue文面のhuman authority | 全文または対象範囲のhuman transcript review | unclaimed | editorial/human owner |
| source画質 | production候補として十分か | 640x360出力のproduction基準と実見 | unaccepted | production owner |
| rights/material use | 利用可能範囲 | 権利者条件と利用形態の人間判断 | pending | rights owner |
| portability | 別端末で同一packageを開く | private artifact transfer/store方針 | unavailable | user-owned infra decision |
| public/publishing | 公開可能性 | 上記gateとmetadata/upload判断 | closed | publication owner |

## 先へ進める目標提案

現時点の最遠目標は「汎用caption renderer完成」ではなく、source固有の修復を比較可能な
portfolio evidenceへ変換し、共有可能なruleと例外を識別することである。

| 段階 | 目標 | 完了条件 | 次に解禁されること |
|---|---|---|---|
| G0 Verify | current exact SHAをaccept/reframe/reject | 上の一問への明示回答とSHA-bound receipt | OUT-09 closureまたは追加修復の正当化 |
| G1 Audit | OUT-06 wrap debtを独立再現 | 2 testのauthority、原因、修正/期待値更新方針を確定 | shared text measurementの信頼回復 |
| G2 Compare | 3–5の異なるsourceでcaption-free cropとshort-cue segmentationをdata-only比較 | source解像度、caption band、cue統計、crop conflict、human resultを同じschemaで収集 | common rule候補とsource-specific overrideの分離 |
| G3 Exception | cropが重要内容と衝突するsourceでopaque matte fallbackを検証 | mask/blurなし、重要内容と字幕可読性を両立、1回render budgetでreadback | fail-closed fallback contract |
| G4 Portfolio | human-reviewed 3–5本を一つのevidence packetへ束ねる | success/failure率、既知例外、性能、画質、rights境界を比較 | production limitation-lift packetの設計 |
| G5 Decision | production subtitle/render readinessを別gateで判断 | representative sources、low-end/physical-device、rights、operator workflowの受入 | production候補化の可否。public/publishingはなお別gate |

直近の推奨はG0。並行して実装を増やすより、current SHAの人間判断を先に確定する方が
次source比較の評価軸を安定させる。G0 accept後はG1とG2が独立の入口になる。G3以降は、
実際のcrop conflictまたは十分なportfolio dataが得られるまでproposal/data-onlyに留める。
