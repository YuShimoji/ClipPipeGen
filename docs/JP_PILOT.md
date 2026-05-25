# JP-Pilot-01 — Japanese Public VOD Diagnostic

`JP-Pilot-01` は、ED-07c 後の日本語 public VOD で `source media -> material_ledger / receipt -> transcript.json -> edit_pack.json -> subtitles -> diagnostic render -> NLE CSV` を通し、制作上どこが詰まるかを観測する slice。これは production / creative / publish acceptance ではなく、`production_candidate=false` の診断である。

ED-09 follow-up: transcript review / correction の CLI と readback は実装済み。次はこの JP-Pilot ignored artifact に小さな review patch を当て、補正済み transcript から cuts / subtitles / NLE / diagnostic render を再生成して、production render へ進めるか STT provider 比較へ戻るかを判断する。

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

## 観測した制作上の詰まり

日本語 Vosk model は pipeline 接続としては機能したが、実コンテンツの字幕品質にはまだ届かない。transcript の例は「話者 も 欲しい ねぇ じゃあ を よ ねー 何 と もう 一 台 です かー...」のように、単語の拾い方はあるものの、人間がそのまま字幕・cut 判断に使える品質ではない。この観測を受けて ED-09 で transcript review / correction の入口を追加済みで、残る観測点は補正済み transcript を downstream に戻した時の改善幅。

cut も 6 件中 3 件が `needs_review` で、HoloEN-01 と同じく「自動候補は出るが、発話境界と内容判断を人が見る必要がある」段階にある。ここで context threshold だけを先に調整すると、低品質 transcript に合わせた局所最適になりやすい。

## 機能停滞の棚卸し

| 領域 | 現在状態 | 停滞の種類 | 推奨する次の動き |
|---|---|---|---|
| STT 品質・補正 | JP public VOD で 26 segments 生成、ただし字幕品質は未受容。ED-09 で補正 CLI は追加済み | 制作判断に使えるかは補正済み rerun の観測待ち | 小さな review patch を当て、cuts / subtitles / NLE / render を再生成して改善幅を見る |
| cut review | 6 candidates のうち 3 needs_review | 自動候補は出るが、境界確認が人手依存 | 補正済み transcript で needs_review 数と context notes が減るか確認する |
| production render / subtitle design | diagnostic render は通るが、本番字幕設計・safe-area・typography は未実装 | transcript/cut が未受容のため先に進むと手戻りが大きい | corrected rerun 後に production subtitle/render acceptance を切る |
| GUI fetch / render / export | CLI は進んだが GUI action は手動 cut 入力中心 | operator 導線の摩擦。core pipeline の停滞ではない | CLI artifact が安定してから GUI に fetch/render/export actions を追加 |
| Publishing / OAuth / visibility | PB / INT-01 は proposed | 認証・API 契約・公開判断が必要なため意図的に後回し | production candidate が作れるまで着手しない |
| TH-01 walkthrough | ソフト実装 done、実 YMM4 template acceptance は user-owned | 実素材/テンプレ準備待ち | 低リスクで閉じるなら walkthrough smoke を別作業に切る |
| SH-02 episode_pack | proposed | artifact が増えたため価値は上がったが、publish_draft がまだ無い | corrected rerun または production render 後にまとめる |
| bg removal / TTS / auto thumbnail | proposed / future | 現在の中核 bottleneck ではない | JP pipeline の字幕・cut 受容後に必要性を再評価 |
| INT-02 parent umbrella | child slices は多数 done、親は proposed のまま | registry 表現の drift。実装停滞ではない | Audit slice で umbrella status を successor-lane 相当に整理する |

## 次の取っ掛かり

| 入口 | 何が軽くなるか | 選ぶと可能になること |
|---|---|---|
| Advance: JP-Pilot corrected rerun | ED-09 の補正入口が実コンテンツで効くか確認できる | corrected transcript から cuts / subtitles / NLE / render を再生成し、production render と STT 比較のどちらを優先するか決められる |
| Verify: STT provider comparison | Vosk の限界と代替 provider の効果を比較できる | whisper.cpp / OpenAI Whisper の依存追加や API 契約変更を根拠付きで判断できる |
| Audit: registry / docs drift cleanup | done child と proposed umbrella のズレが減る | 次スライス選定時に「実装済みだが未受容」と「本当に未実装」を混同しなくなる |
| Explore: GUI action expansion | CLI 操作の摩擦が減る | fetch / render / export を operator が画面から実行できる |
