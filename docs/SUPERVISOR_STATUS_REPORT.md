# 監修AI向け現状報告 — OUT-11 human-review repairs ready

更新日: 2026-07-21

branch: `codex/out-11-five-source-short-portfolio-wave-v0`

状態: `OUT11_HUMAN_REVIEW_REPAIRS_COMBINED_REVIEW_READY`

remote再開境界: 検証済み実装head
`249b3308b0d8a1cc8b75d37a245d717322859133`を基準に、active branch
`codex/out-11-five-source-short-portfolio-wave-v0`へhandoff docsを同期する。別端末ではfetch、
branch switch、ff-only pull後に`docs/CURRENT_HANDOFF.md`を読む。Gitでportableなのはcode/docs/tests、
exact identity、判断契約までで、ignored `episodes/`のmedia/QA/review packageは同一マシン限定である。

## 到達した状態

OUT-11初回combined reviewの人間観測を、当時のOUT-10・SOURCE-04・SOURCE-05 exact SHAへ
結び付けた。SOURCE-04は「一本として自然、追加違和感なし」を当該bytesだけの
`accepted_internal`として記録し、媒体を変更していない。OUT-10とSOURCE-05は人間が指摘した
終端欠陥を旧候補lineageへ残し、source近傍の映像、字幕、waveform、shot transition、テロップ、
動作を先に観測してから、それぞれ一回の実renderで修復した。

最終review面は修復二本だけ。SOURCE-04は受領証としてexact SHA/sizeを表示するが、MP4は統合
packageへ複製せず再視聴を要求しない。OUT-08/09もaccepted comparison contextのままで、winner、
共通caption/crop/speaker-color policy、rights、production、thumbnail、public/publishingは閉じている。

## 人間判断から修復までの対応

| 対象 | 人間観測をbindした旧実体 | 実媒体から確定した問題 | 実施した処理 | 現在状態 |
|---|---|---|---|---|
| OUT-10 | `a53d0416...134f2`, 16,821,370 bytes, `0.000–30.014s` | 導入は成立するが、30.014sから意識確認場面が始まり、反応・台詞が未完 | 導入・字幕46 cue・音声方針・neutral matteを維持し、34.785sまでの4 cueだけ追加 | 新SHA `62d4b45b...97cdd`、human review pending |
| SOURCE-04 | `465d732c...16524`, 8,523,260 bytes, `0.000–18.500s` | 明確な追加問題なし | render/remux/transcode/editなし。accepted receiptへ移動 | 同じSHA/size、`accepted_internal` |
| SOURCE-05 | `370850c5...b578`, 4,805,101 bytes, `202.586–217.650s` | 新画面直後で停止。歌唱・歌詞・音楽句という旧説明は知覚証拠なし | 同一recordingの開始を維持し、card列、illustration列、card table、title/credit holdをsource EOFまで収録 | 新SHA `b4a01413...a4969`、human review pending |

SOURCE-05はBGM・映像中心の候補として扱う。official ID JSON3はtimed-text landmarkに限定し、
speaker count、歌唱、歌詞、native lyricの意味をcurrent metadata、scorecard、review copyで主張しない。

## 終端根拠

### OUT-10

30.014sは「意識確認、開始」の開始点で、31.749–33.584sも「大丈夫ですか」「息してますか」と
患者反応が進行中。34.785sで「ゴッドハンドやね」のパンチラインと反応が完了し、34.800sから
別キャラクター紹介へ切り替わる。選択したsemantic rangeは`0.000–34.785s`であり、次sceneの
数frameを終了記号として使っていない。

### SOURCE-05

旧217.650sは新しいcard画面へ切り替わった直後だった。同じsourceをEOFまで観測すると、
card sequence、illustrated-character montage、final card table、title/credit holdが連続し、音声も
末尾へ自然に減衰する。開始`202.586s`を維持し、source EOF `260.643s`をsemantic endに選んだ。
最終0.766667sの暗部はsource-native fadeで、blackdetect上限1.5s内。人工fade、黒画面、freeze、
終了card、無音は追加していない。

## Exact成果物

| artifact_id | repo-relative path | exact identity / 開き方 |
|---|---|---|
| `clip-out10-third-source-short-portfolio-expansion-v0-001` | `episodes/out10_hololive_secret_clinic_20260719/review/out10_third_source_short_portfolio/` | MP4 `62d4b45b26c2833e8a939a8f3d1954a4ea79047436f08d8f999269b539697cdd`; readback `77e6c578...75c53`; manifest `093d7355...71e80` |
| `clip-out11-source04-indonesia-laugh-short-v0-001` | `episodes/out11_source04_indonesia_laugh_20260720/review/out11_source04_candidate/` | accepted unchanged MP4 `465d732c05cf29f42e89c5b0564a0d6a15f3814b70073ff9039a27a93f916524`; 8,523,260 bytes |
| `clip-out11-source05-dramatic-xviltration-short-v0-001` | `episodes/out11_source05_dramatic_xviltration_20260720/review/out11_source05_candidate/` | MP4 `b4a01413202e3e177a11dc42754d38f5a4b7b10cd7c7bec0aa43536d440a4969`; readback `38ad9b1b...29129`; manifest `c431fa1a...98388` |
| `clip-out11-five-source-short-portfolio-wave-v0-002` | `episodes/out11_five_source_short_portfolio_20260720/review/out11_five_source_short_portfolio/` | localhost `http://127.0.0.1:8074/index.html`; 2 media / 1 receipt / 5 rows / 1 question |
| final-six-second QA | `episodes/out11_five_source_short_portfolio_20260720/qa/human_review_repair_final6_20260721/` | OUT-10/SOURCE-05 contact sheets and PCM waveforms; ignored local evidence |

combined readback SHAは`4e6160915d80bdcef58cfa407e6be3e74daf4be002dc14d2a9b02f6fda54b406`、
scorecard SHAは`4b388531fb3093fd10449d7722656d2ea8dcae8bf9e4d0783d0b63f61ed0d2c9`、
manifest file/self SHAは`e72de3fe092aafb72aa7dd59208c2c07e715c307ce9aac92ada61ae8e632a390` /
`58276967cb2328f3a8b9ea8813bb85a4847f84e26e8bd465206c56d3e87da7bd`。

## Media・runtime検証

| 検証 | OUT-10 | SOURCE-05 | 結果の意味 |
|---|---|---|---|
| output | H.264/AAC 1080x1920 30fps yuv420p, 34.800s | H.264/AAC 1080x1920 30fps yuv420p, 58.000s | delivery candidate形式は機械pass |
| decode / faststart | pass / moov before mdat | pass / moov before mdat | 全尺decodeとstream配置pass |
| loudness | `-13.79 LUFS / -1.45 dBTP` | `-14.02 LUFS / -1.49 dBTP` | internal candidate QA帯。production mix承認ではない |
| signal | black 0 / silence 0 | black 0.766667s < 1.5s / silence 0 | 欠落や人工無音のcritical blockなし |
| caption | official 50 cue、containment pass、final 34.785s | overlay 0、source-native text retained、意味未確認 | SOURCE-05 lyric claimなし |
| final 6s | 意識確認→患者反応→最終台詞を連続frameで確認 | montage→title/credit→source fadeを確認 | semantic acceptanceはなお人間判断 |

localhostではindex HTTP 200、OUT-10/SOURCE-05ともRange 206。desktop 1280とmobile 390で
horizontal overflowなし、二mediaはreadyState 4/error null。clean URLは両方paused/muted/
currentTime 0、明示`?qa-playback=1`だけ先頭をmuted再生し、SOURCE-05再生時にOUT-10がpauseした。
console warning/error 0。QA後にbrowser tabとserverを停止し、port 8074 listener 0を確認した。

code validationは`uvx --with Pillow pytest -q`が580 passed。`npm ls --depth=0`はElectron
`42.0.0`を読み戻し、通常GUI smokeとElectron smokeもpass。changed-scope Ruff、dashboard JSON
parse、docs dashboard再生成、`git diff --check`もpassし、`git ls-files episodes`は0件である。
同一マシンpackageの二MP4、readback、scorecard、manifestも上記exact SHAと再一致し、cleanup保護対象の
R3 `human_preview_session/`を保持した。

## Code・authority変更

- OUT-10 builderのpredecessorを旧`a53d0416...134f2`へ更新し、4 cue endpoint lineageを固定。
- source-adaptive builderへoptional `repair_lineage`の検証とreadback/manifest出力を追加。
- five-source builderを3 active mediaから2 repair media + 1 accepted receiptへ変更し、SOURCE-04
  media非copy、source range/content/checkpoint表示、明示QA query再生を検証。
- README、Runtime、Current Handoff、OUT-10/11契約、Automation Boundary、Artifact Registry、
  Supervisor report、5-source scorecard、dashboardをcurrent実体へ同期。
- `episodes/`はignoredのまま、`git ls-files episodes`は0を維持。

## 残る判断と最遠の安全な目標

| 入口 | 目的と効果 | 必要条件 | 現在状態 | 次に可能になること |
|---|---|---|---|---|
| Advance | 修復二本のsemantic acceptanceを一回で閉じる | 同じページで二本を見た自由記述 | owner/human待ち | 新SHAごとのaccept / bounded repair / rejectを正確に記録 |
| Verify | SOURCE-05を投資済み理由で温存しない | audio-visual unitに具体的違和感があれば時点を示す | 歌詞推定なし・EOF候補ready | 同一source再修復かpark/rejectを選択 |
| Close | OUT-10/11のbranch closureを順序立てる | 修復二本accept、tracked docs/tests green、監修承認 | 未開始 | OUT-10 closureを先、OUT-11 closureを後にmainへfast-forwardする計画 |
| Audit | 5 sourceの字幕差分をproduction課題として扱う | 候補acceptとは別にproduction subtitle-design gateを開く | deferred | speaker推測なしの字幕比較・設計判断 |
| Release | rights/production/publicを別証拠で閉じる | rights、production render/subtitle/image、thumbnail、publishing各owner承認 | 全て未承認 | 初めてproduction/public release候補へ進める |

現時点の最遠安全目標は「修復二本のexact SHA受理 → OUT-10/OUT-11 closure順序の監修承認 →
main fast-forward計画」まで。rights、production、thumbnail、public/publishingをこの人間レビューから
推論して先回りすることはできない。

## 監修AIが次に守る境界

- SOURCE-04のaccepted bytesとOUT-08/09を再開しない。
- SOURCE-05へ歌唱・歌詞・speaker identityを追加推定しない。
- 二本のacceptanceをwinner、共通caption/crop、rights、production、thumbnail、publicへ拡張しない。
- mediaはsame-machine ignored artifactで、Gitや別hostへportableではない。
- 次の人間判断後、問題のあるcandidateだけを処理し、合格済みcandidateを巻き込まない。
