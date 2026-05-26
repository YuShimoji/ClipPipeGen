# JP-Pilot-01 — Japanese Public VOD Diagnostic

`JP-Pilot-01` は、ED-07c 後の日本語 public VOD で `source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles -> diagnostic render -> NLE CSV` を通し、制作上どこが詰まるかを観測する slice。これは production / creative / publish acceptance ではなく、`production_candidate=false` の診断である。

ED-09 follow-up: `JP-Pilot-01R` / `JP-Pilot-01R2` で transcript review / correction の実効性を確認済み。公式 Japanese subtitle track を照合材料に既存 26 transcript segments を accepted 25 / rejected 1 / unreviewed 0 まで補正し、短め selected cuts 5 本、context 5 passed、21 subtitle drafts、NLE CSV、diagnostic render を再生成した。ED-10 follow-up: `JP-Pilot-01R3` で公式 subtitle track 自体を transcript-compatible artifact として import し、105 segments / 9 selected cuts / 105 subtitle drafts / NLE CSV 9 rows / diagnostic render まで再投入した。これは引き続き diagnostic であり、production / creative / publish acceptance ではない。

## 対象素材

| 項目 | 内容 |
|---|---|
| URL | <https://www.youtube.com/watch?v=7J5aS_pcBj4> |
| Title | `【アニメ】押忍！！ば～んちょ だじぇ！` |
| Source | `hololive ホロライブ - VTuber Group` official channel |
| Duration | 164.77s |
| 選定理由 | 公式チャンネルの公開短尺アニメ。members-only / paid / concert / song / gameplay / 第三者 IP 高リスクの候補を避け、診断用に短く扱いやすい素材として採用した。 |
| 境界 | rights は readback。COVER / YouTube の公開素材を診断 pipeline に通すだけで、Content ID 登録、再公開、creative acceptance、publishing acceptance には進まない。 |

## Smoke 結果（2026-05-25 JST）

Ignored episode: `episodes/jp_pilot01_hololive_bancho_20260525`

| 工程 | readback |
|---|---|
| `fetch-source-video --mode yt-dlp-video` | `source_video.mp4`、h264/aac、1920x1080、30fps、164.77s、ledger 登録済み |
| `fetch-source-audio --mode yt-dlp-audio` | `source.wav`、pcm_s16le、16kHz、mono、sha256 `7cd566dc62683651b05b10b1b4397c44699807249f90af784b88ba0f572cae5d` |
| `transcribe-audio --engine vosk --language ja --model vosk-model-small-ja-0.22` | 26 segments、audio duration 164.71s、segment duration 合計 84.67s、speech coverage 約 51.4%、`real_transcript=true`、language/model check passed |
| `generate-cuts --target-duration-seconds 15 --gap-threshold-seconds 2.5 --max-candidates 6 --select-generated` | 6 cut candidates / 6 selected |
| `check-cut-context --selected-cuts-only` | 3 passed / 3 needs_review / 0 failed |
| `generate-subtitles --wrap-eaw 40 --selected-cuts-only` | 17 subtitle drafts、`source_type=real_transcript`、9 segments skipped outside selected cuts |
| `render-tiny-proof --burn-in-subtitles diagnostic` | `rendered_video.mp4`、6.6s、1920x1080、h264/aac、subtitle burn-in enabled、`production_candidate=false` |
| `export-nle` | `nle_cut_list.csv` 6 rows、manifest/report generated、`production_edit_candidate=false` |
| `audit-material-ledger` | `ok=true`、issues `[]`、materials `2` |

## ED-09 follow-up: JP-Pilot-01R corrected rerun（2026-05-26 JST）

Ignored episode 内で raw Vosk transcript / edit_pack を backup し、`transcript_review_patch_jp_pilot01r.json` を `review-transcript` に通した。補正 text は YouTube 公式 Japanese subtitle track `7J5aS_pcBj4.ja.json3` と対象動画フレームを照合できた範囲だけに限定した。

| 観測項目 | raw Vosk JP | JP-Pilot-01R corrected |
|---|---:|---:|
| transcript review counts | unreviewed 26 / accepted 0 | unreviewed 19 / accepted 7 |
| cut candidates / selected | 6 / 6 | 5 / 5 |
| context check | 3 passed / 3 needs_review | 3 passed / 2 needs_review |
| subtitle drafts | 17 | 26 |
| NLE CSV rows | 6 | 5 |
| diagnostic render | 6.6s / 1080p / subtitles enabled | 6.6s default render + 10.0s focus render for corrected `cut_003` |
| rights readback | skeleton pending with schema issues | schema-readable `pending` with source / talent / disclosure readback |

重要な観測: ED-09 の patch 経路は機能し、`status-episode` / `export-nle` も review state を読めた。一方、部分補正だけでは selected cuts がまだ広く、補正外の raw Vosk text が subtitle draft に混ざる。次は production render 直行ではなく、補正 coverage と selected cut narrowing を進めるか、公式 subtitle track import / STT provider comparison を切る判断が必要。

## JP-Pilot-01R2: review coverage + selected cut narrowing（2026-05-26 JST）

R2 では R1 の default `transcript.json` / `edit_pack.json` を ignored backup に残し、公式 Japanese subtitle track の各 event を Vosk segment へ max-overlap で割り当てた。割り当て可能な既存 segment は `accepted`、独立した公式字幕 event が割り当たらない `seg_000009` は filler / duplicate timing noise として `rejected` にした。公式字幕 event 37 件は Vosk segment と十分に重ならず、ED-09 patch だけでは表現できないため、top-level `review.status` は conservative に `needs_review` のまま。

| 観測項目 | JP-Pilot-01 raw | JP-Pilot-01R | JP-Pilot-01R2 |
|---|---:|---:|---:|
| transcript review counts | unreviewed 26 / accepted 0 / rejected 0 | unreviewed 19 / accepted 7 / rejected 0 | unreviewed 0 / accepted 25 / rejected 1 |
| cut candidates / selected | 6 / 6 | 5 / 5 | 5 / 5 |
| selected cut duration | 6.6s〜18.5s | 3.6s〜66.6s | 10.9s〜23.1s |
| context check | 3 passed / 3 needs_review | 3 passed / 2 needs_review | 5 passed / 0 needs_review |
| subtitle drafts | 17 | 26 | 21 |
| NLE CSV rows | 6 | 5 | 5 |
| diagnostic render | 6.6s / 1080p | 6.6s default + 10.0s focus | 23.13s / 1080p / clamped=false |

R2 の成果は「既存 Vosk segment の補正 coverage」と「selected cut の広さ」はかなり改善できたこと。一方で、公式 subtitle track には Vosk が segment 化しなかった短い発話やリアクションが残る。ここは `review-transcript` ではなく、公式 subtitle track import / transcript alignment の仕事として切り出すのが自然。

## JP-Pilot-01R3: official subtitle track import rerun（2026-05-26 JST）

R3 では ED-10 の `import-subtitle-track` を使い、YouTube JSON3 の公式 Japanese subtitle track を `transcript.json` 互換 artifact として再投入した。R2 の default `transcript.json` / `edit_pack.json` は ignored backup に残し、imported transcript は `stt.engine="subtitle_track"` / `provider="youtube_subtitles"` / `review.status="needs_review"` / `reviewed_by="codex:jp-pilot01r3"` として保存した。これは字幕 track の pipeline 取り込み確認であり、字幕デザインや production acceptance ではない。

| 観測項目 | JP-Pilot-01 raw | JP-Pilot-01R2 | JP-Pilot-01R3 |
|---|---:|---:|---:|
| transcript source | Vosk JP | Vosk JP + ED-09 review patch | official subtitle track import |
| transcript segments | 26 | 26 | 105 |
| transcript review counts | unreviewed 26 / accepted 0 / rejected 0 | unreviewed 0 / accepted 25 / rejected 1 | unreviewed 0 / accepted 105 / rejected 0 |
| cut candidates / selected | 6 / 6 | 5 / 5 | 9 / 9 |
| context check | 3 passed / 3 needs_review | 5 passed / 0 needs_review | 3 passed / 6 needs_review |
| subtitle drafts | 17 `real_transcript` | 21 `real_transcript` | 105 `imported_subtitle_track` |
| NLE CSV rows | 6 | 5 | 9 |
| diagnostic render | 6.6s / 1080p | 23.13s / 1080p / clamped=false | 6.84s / 1080p / clamped=false |

R3 で R2 の最大停滞だった「Vosk segment 外に落ちた公式字幕 event を artifact に戻せない」問題は解消した。一方、公式字幕は短い event を細かく保持するため、自動 cut は 9 本に増え、context check は 6 本が needs_review になった。次の判断は transcript completeness ではなく、final cut/context review と production subtitle/render acceptance に移っている。公式字幕がない素材では、引き続き STT provider comparison が優先候補になる。

R3 review packet: `build-cut-review-packet` で `episodes/jp_pilot01_hololive_bancho_20260525/review/jp_pilot01r3_cut_review/` に `cut_review_packet.json` / `cut_review_report.html` / `evidence_summary.json` / `evidence_summary.html` を生成済み。各 cut には duration、reason、context notes、subtitle event count、subtitle density、review focus、`decision_placeholder.final_decision="undecided"` が入る。これは final cut 採否ではなく、人間レビューへ渡すための readback。

## 観測した制作上の詰まり

R3 update: 公式 subtitle track の欠落回収は ED-10 で進んだ。現時点の詰まりは、R3 の 9 cuts 中 6 cuts が context `needs_review` であること、production subtitle design / safe-area / typography / full render policy が未定であること、公式字幕が無い素材では Vosk 以外の STT provider 比較がまだ必要なこと。

日本語 Vosk model は pipeline 接続としては機能したが、実コンテンツの字幕品質にはまだ届かない。JP-Pilot-01R2 では公式 subtitle track を使った補正により、既存 transcript segment の範囲では unreviewed を解消し、selected cut context も全件 passed にできた。ただし公式字幕 event の一部は Vosk segment 外に落ちるため、caption completeness はまだ未受容。

cut は R2 で 5 件すべて `passed` になり、60 秒級の広い window も 10〜23 秒台へ縮んだ。ここから先の停滞は context threshold ではなく、「公式字幕の欠落 event をどう transcript/subtitle artifact に取り込むか」と「production subtitle design をどこまで定義するか」に移っている。

## 機能停滞の棚卸し

| 領域 | 現在状態 | 停滞の種類 | 推奨する次の動き |
|---|---|---|---|
| STT 品質・補正 | JP-Pilot-01R2 で既存 26 segments は accepted 25 / rejected 1 / unreviewed 0 | Vosk segment に載らない公式字幕 event が残る | official subtitle track import / transcript alignment を切る |
| cut review | R2 で 5 selected cuts、5 passed / 0 needs_review、10.9s〜23.1s | 境界 readback は改善。creative choice はまだ未受容 | import/alignment 後に final selected cut policy を決める |
| production render / subtitle design | 23.13s diagnostic render は clamped=false で通るが、本番字幕設計・safe-area・typography は未実装 | caption completeness と design acceptance が未定 | caption import で欠落を埋めてから production subtitle/render acceptance を切る |
| GUI fetch / render / export | CLI は進んだが GUI action は手動 cut 入力中心 | operator 導線の摩擦。core pipeline の停滞ではない | CLI artifact が安定してから GUI に fetch/render/export actions を追加 |
| Publishing / OAuth / visibility | PB / INT-01 は proposed | 認証・API 契約・公開判断が必要なため意図的に後回し | production candidate が作れるまで着手しない |
| TH-01 walkthrough | ソフト実装 done、実 YMM4 template acceptance は user-owned | 実素材/テンプレ準備待ち | 低リスクで閉じるなら walkthrough smoke を別作業に切る |
| SH-02 episode_pack | proposed | artifact が増えたため価値は上がったが、publish_draft がまだ無い | caption import または production render 後にまとめる |
| bg removal / TTS / auto thumbnail | proposed / future | 現在の中核 bottleneck ではない | JP pipeline の字幕・cut 受容後に必要性を再評価 |
| INT-02 parent umbrella | child slices は多数 done、親は proposed のまま | registry 表現の drift。実装停滞ではない | Audit slice で umbrella status を successor-lane 相当に整理する |

## 次の取っ掛かり

R3 後の入口は、`Explore: subtitle track import` ではなく `Advance: final cut/context review` と `Advance: production subtitle/render acceptance` が先頭になる。公式字幕が無い素材に進む場合だけ、`Verify: STT provider comparison` を優先する。

| 入口 | 何が軽くなるか | 選ぶと可能になること |
|---|---|---|
| Explore: subtitle track import | Vosk segment 外に落ちた公式字幕 event を artifact に戻せる | ED-10 相当の caption import / transcript alignment を設計できる |
| Advance: production subtitle/render acceptance | R2 の narrowed cuts を使って typography / safe-area / full render policy を検討できる | ただし caption gap の扱いを先に決める必要がある |
| Verify: STT provider comparison | 公式 subtitle が無い素材で Vosk の限界と代替 provider の効果を比較できる | whisper.cpp / OpenAI Whisper の依存追加や API 契約変更を根拠付きで判断できる |
| Audit: registry / docs drift cleanup | done child と proposed umbrella のズレが減る | 次スライス選定時に「実装済みだが未受容」と「本当に未実装」を混同しなくなる |
| Explore: GUI action expansion | CLI 操作の摩擦が減る | fetch / render / export を operator が画面から実行できる |
