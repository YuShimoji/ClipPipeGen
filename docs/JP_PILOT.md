# JP-Pilot-01 — Japanese Public VOD Diagnostic

`JP-Pilot-01` は、ED-07c 後の日本語 public VOD で `source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles -> diagnostic render -> NLE CSV` を通し、制作上どこが詰まるかを観測する slice。これは production / creative / publish acceptance ではなく、`production_candidate=false` の診断である。

ED-09 follow-up: `JP-Pilot-01R` で transcript review / correction の実効性を確認済み。公式 Japanese subtitle track を照合材料に 7 segments を accepted にし、補正済み transcript から cuts / subtitles / NLE / diagnostic render を再生成した。これは引き続き diagnostic であり、production / creative / publish acceptance ではない。

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

## 観測した制作上の詰まり

日本語 Vosk model は pipeline 接続としては機能したが、実コンテンツの字幕品質にはまだ届かない。JP-Pilot-01R では公式 subtitle track を使った部分補正により、少なくとも補正済み segment は downstream に戻せることを確認した。ただし 19/26 segments は未補正のままで、全体の制作判断にはまだ不十分。

cut も 6 件中 3 件が `needs_review` で、HoloEN-01 と同じく「自動候補は出るが、発話境界と内容判断を人が見る必要がある」段階にある。ここで context threshold だけを先に調整すると、低品質 transcript に合わせた局所最適になりやすい。

## 機能停滞の棚卸し

| 領域 | 現在状態 | 停滞の種類 | 推奨する次の動き |
|---|---|---|---|
| STT 品質・補正 | JP-Pilot-01R で 7 segments accepted、19 segments unreviewed | ED-09 経路は通ったが、全体 coverage は不足 | 公式 subtitle import / 追加 review pass / provider 比較を選ぶ |
| cut review | corrected rerun で 5 cuts、2 needs_review | needs_review は減ったが selected cuts がまだ広い | 補正 coverage を増やし、selected cut narrowing を行う |
| production render / subtitle design | default / focus diagnostic render は通るが、本番字幕設計・safe-area・typography は未実装 | transcript/cut がまだ production 受容前 | review coverage と cut narrowing 後に production subtitle/render acceptance を切る |
| GUI fetch / render / export | CLI は進んだが GUI action は手動 cut 入力中心 | operator 導線の摩擦。core pipeline の停滞ではない | CLI artifact が安定してから GUI に fetch/render/export actions を追加 |
| Publishing / OAuth / visibility | PB / INT-01 は proposed | 認証・API 契約・公開判断が必要なため意図的に後回し | production candidate が作れるまで着手しない |
| TH-01 walkthrough | ソフト実装 done、実 YMM4 template acceptance は user-owned | 実素材/テンプレ準備待ち | 低リスクで閉じるなら walkthrough smoke を別作業に切る |
| SH-02 episode_pack | proposed | artifact が増えたため価値は上がったが、publish_draft がまだ無い | review coverage または production render 後にまとめる |
| bg removal / TTS / auto thumbnail | proposed / future | 現在の中核 bottleneck ではない | JP pipeline の字幕・cut 受容後に必要性を再評価 |
| INT-02 parent umbrella | child slices は多数 done、親は proposed のまま | registry 表現の drift。実装停滞ではない | Audit slice で umbrella status を successor-lane 相当に整理する |

## 次の取っ掛かり

| 入口 | 何が軽くなるか | 選ぶと可能になること |
|---|---|---|
| Advance: JP-Pilot review coverage | 19 unreviewed segments を減らし、selected cuts を短くできる | production subtitle/render acceptance に進めるだけの素材を作れる |
| Explore: subtitle track import | 公式 subtitle track がある素材では手補正コストを大きく減らせる | ED-10 相当の caption import / transcript alignment を設計できる |
| Verify: STT provider comparison | 公式 subtitle が無い素材で Vosk の限界と代替 provider の効果を比較できる | whisper.cpp / OpenAI Whisper の依存追加や API 契約変更を根拠付きで判断できる |
| Audit: registry / docs drift cleanup | done child と proposed umbrella のズレが減る | 次スライス選定時に「実装済みだが未受容」と「本当に未実装」を混同しなくなる |
| Explore: GUI action expansion | CLI 操作の摩擦が減る | fetch / render / export を operator が画面から実行できる |
