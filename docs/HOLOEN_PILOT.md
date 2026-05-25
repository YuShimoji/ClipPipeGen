# HoloEN-01 — Phase 0.5 publish-quality diagnostic pilot

**状態**: `done`（初回 actual smoke 完了、commit を参照）

`Phase 0.5` は、`Phase 0` で plumbing が通ったあとに、**英語発話コンテンツで「投稿候補品質」が成立しそうかを早期観測する** 先行路線。日本語 STT 対応（`JP-STT-01`）の代替ではなく、品質の早期診断を先に置くもの。

## 運用方針（自律選定）

assistant は HoloEN public VOD 候補を **自律的に調査・選定し、risk が低いと判断した 1 本を diagnostic smoke の default として使う**。operator review は事後で良い。

過去 commit に存在した「assistant は任意 URL を勝手に選定しない」「actual smoke は user-supplied URL を待つ」記述は **撤廃**。INVARIANTS の "rights は readback、hard gate にしない" との一貫性を取った。除外条件（後述）は **compliance であって safety ではない** ので維持する。

### 自律選定の手順

1. **候補列挙**: `yt-dlp --flat-playlist --playlist-end 25 --print "%(id)s|%(title)s|%(duration_string)s|%(availability)s" "https://www.youtube.com/@<HoloEN-talent>/videos"` で talent の最近 25 本を取得
2. **avoid-list で除外**: title に `members` / `membership` / `song` / `cover` / `mv` / `concert` / `sing` / `unarchived` 含むものを除外、`availability != 'public'` を除外
3. **risk 評価**: talent オリジナル content（animation、voice acting、green screen など）を優先。ゲーム配信 / 楽曲を含むものは第三者 IP リスクで後回し
4. **長さ**: 1〜30 分程度が smoke に丁度良い（diagnostic render は最初の selected cut のみなので長尺は不要）
5. **1 本選定**: rationale を docs / commit message に書く

operator が後で「別 URL でやり直したい」と言えば、その URL で smoke を再実行する。

## 何ではないか

- production / creative / publish acceptance ではない
- commercial product validation ではない
- YouTube upload / publishing / OAuth / visibility / thumbnail set には進まない
- Content ID 登録には進まない
- 日本語 STT 対応の代替ではない
- font / typography / safe-area polish ではない
- transcript correction UI ではない
- GUI render button / FCPXML / Resolve XML ではない

## 何であるか

- `Phase 0` で証明済みの縦糸（URL → source_video / source_audio → transcript → edit_pack → rendered_video.mp4 → NLE CSV）を **HoloEN 英語発話 VOD** で 1 本通す
- 出力 artifact を operator が見て、**動画コンテンツとして成立しそうか** を技術 / 制作 / 権利の 3 軸で評価する
- 観測結果をもとに、`JP-STT-01` / `transcript review` / `production render acceptance` のいずれを Phase 1 に置くかを判断する

## URL 選定条件（positive）

HoloEN pilot に使う URL は、assistant が自律選定してよい。operator が別 URL を指定した場合は、その明示 URL を優先する。どちらの場合も以下の条件を満たすことを readback する。

- COVER / hololive production の **HoloEN 所属 talent の公開済み VOD**
- 公式 YouTube channel の **public** 視聴可能なもの（unlisted / private ではない）
- **archive / 通常配信切り抜き** が中心で、英語発話の比率が高い場面を含む
- 10〜60秒 程度で切り出せそうな英語発話シーンが含まれる
- 公開済み URL とタイトルが明示できる

## 避けるべき素材（negative）

COVER 公式 derivative works guidelines（[hololivepro.com/en/terms/](https://hololivepro.com/en/terms/)）で **clip 不可** と明示されているものを除外する。

- **members-only video**
- **paid content / pay-per-view**
- **concert footage**
- **歌唱・ライブ・楽曲中心の素材**（third-party music IP リスク）
- **コラボ配信で第三者 talent の動画ガイドラインも別途確認が必要なもの**（一次素材所属確認が困難な場合）
- **ゲーム配信のうち、ゲーム会社側で配信・二次利用が制限されているタイトル**

ゲーム配信を選ぶ場合は、ゲーム会社側の **配信・二次利用ガイドライン** が公開されている / かつ二次利用許可がある対象に限る。判断が付かない場合は選定しない。

## COVER 公式 attribution / 禁止事項（要点抜粋）

正本: <https://hololivepro.com/en/terms/>

- clip / shorts / translation は guideline 準拠なら個別許諾不要だが、**clip に対する Content ID 登録は禁止**
- **paid / members-only / concert は guideline 範囲外、明示的に clip 不可**
- 公開時は **元配信 URL link** と **元配信 source title** を attribution として明記する
- 楽曲派生は `"Song: [Title] / Artist: hololive IDOL PROJECT"` 形式
- 第三者 IP（fonts / images / music / source code / game）の terms 解釈は COVER が答えない。**operator が個別に確認する**
- 公序良俗違反 / 政治・宗教コンテンツ / talent や第三者の名誉毀損は禁止
- official かのように偽装することは禁止

これらは **operator readback** として `description_draft_candidate` / `rights_manifest.warnings[]` に残し、`set-compliance` で値だけによる hard gate は掛けない（既存 INVARIANTS 維持）。

## Runbook（assistant 選定または operator 指定 URL があるとき）

前提:
- main / origin/main 同期、working tree clean
- yt-dlp / ffmpeg / ffprobe が PATH または `--*-path` で解決可能
- Vosk Python と vosk-model-small-en-us-0.15 が `_tmp/stt_models/` 等に展開済み（Phase 0 と同じ）

```powershell
# 0. operator 変数
$EP="holoen_pilot_<date>"   # ignored episode id
$MID_V="src_video_holoen_pilot"
$MID_A="src_audio_holoen_pilot"
$URL="<assistant-selected-or-operator-supplied HoloEN public VOD URL>"
$YTDLP="<resolved yt-dlp path>"
$FFMPEG="<resolved ffmpeg path>"
$FFPROBE="<resolved ffprobe path>"
$VOSK="_tmp/stt_models/vosk-model-small-en-us-0.15"

# 1. episode skeleton + rights manifest with source URL/title
python -m src.cli.main init-episode --episode-id $EP

# 2. dry-run video fetch (no network) — readback URL scrub / format selector / allowed containers
python -m src.cli.main fetch-source-video --mode yt-dlp-video `
  --episode-id $EP --material-id $MID_V `
  --source-url $URL `
  --yt-dlp-path $YTDLP --ffprobe-path $FFPROBE `
  --dry-run

# 3. actual fetch
python -m src.cli.main fetch-source-video --mode yt-dlp-video `
  --episode-id $EP --material-id $MID_V `
  --source-url $URL `
  --yt-dlp-path $YTDLP --ffprobe-path $FFPROBE

# 4. source audio fetch from same URL
python -m src.cli.main fetch-source-audio --mode yt-dlp-audio `
  --episode-id $EP --material-id $MID_A `
  --source-url $URL `
  --yt-dlp-path $YTDLP --ffmpeg-path $FFMPEG

# 5. Vosk EN transcript (via uvx --with vosk)
uvx --with vosk python -m src.cli.main transcribe-audio `
  --episode-id $EP `
  --source-audio episodes/$EP/materials/$MID_A/source.wav `
  --output episodes/$EP/transcript.json `
  --engine vosk --model $VOSK `
  --language en `
  --material-ledger episodes/$EP/material_ledger.json `
  --material-id $MID_A

# 6. edit_pack + cuts + context + subtitles
python -m src.cli.main init-edit-pack --episode-id $EP
python -m src.cli.main generate-cuts `
  --transcript episodes/$EP/transcript.json `
  --edit-pack episodes/$EP/edit_pack.json `
  --target-duration-seconds 12 --select-generated
python -m src.cli.main check-cut-context `
  --transcript episodes/$EP/transcript.json `
  --edit-pack episodes/$EP/edit_pack.json
python -m src.cli.main generate-subtitles `
  --transcript episodes/$EP/transcript.json `
  --edit-pack episodes/$EP/edit_pack.json `
  --wrap-eaw 40 --selected-cuts-only

# 7. diagnostic render (first selected cut, subtitle burn-in diagnostic)
python -m src.cli.main render-tiny-proof `
  --episode-id $EP `
  --source-video-material-id $MID_V `
  --source-audio-material-id $MID_A `
  --edit-pack-path episodes/$EP/edit_pack.json `
  --output-id holoen_pilot_render `
  --burn-in-subtitles diagnostic `
  --ffmpeg-path $FFMPEG --ffprobe-path $FFPROBE

# 8. NLE CSV export
python -m src.cli.main export-nle `
  --edit-pack episodes/$EP/edit_pack.json --format json

# 9. ledger audit
python -m src.cli.main audit-material-ledger `
  --episode-id $EP --format json
```

artifact はすべて ignored `episodes/$EP/` 配下。`_tmp/` / `episodes/` は `.gitignore` 対象。

## Quality scorecard

operator が rendered artifact / receipt / CSV を見て、3 軸でスコアを付ける。`pass` / `weak` / `fail` または 1〜5 段階。

### 技術評価

| 観点 | 期待 | 評価 |
|---|---|---|
| URL video fetch | exit 0、`audit-material-ledger ok=true` | |
| source video metadata | FFprobe で duration / container / video codec / audio codec / resolution / fps / stream count が揃う | |
| source audio metadata | `source.wav` pcm_s16le / 16kHz / mono | |
| transcript segment count | > 0、長さに対する妥当な比率 | |
| transcript coverage | `sum(segment.duration) / source_duration` の割合 | |
| subtitle draft count | `cut_candidates.count == subtitles.count`（selected_cuts_only モードで対応） | |
| rendered video duration | `selected_cut.duration` に一致（clamp warning 無し） | |
| NLE CSV row count | `selected_cut_count` に一致 | |
| fallback / warning | render fallback なし / 致命 warning なし | |

### 制作評価

| 観点 | 評価ガイド |
|---|---|
| transcript が英語発話を拾っているか | 主要発話の単語が捉えられているか |
| subtitle が自然に読めるか | 単語単位の分断や不自然な改行が無いか |
| cut candidate が面白そうか | 発話の山場と一致しているか |
| 10〜60秒のテンポ | 1 cut が長過ぎ / 短過ぎ / リズム破綻していないか |
| 字幕 burn-in が最低限読める | 位置・コントラスト・サイズが diagnostic として確認できる |
| NLE で手直しすれば投稿候補になりそうか | yes / weak / no |
| 人間レビューが必要な箇所 | tag: transcript / cut boundary / subtitle wrap / overall pacing |

### 権利・運用評価

| 観点 | 評価 |
|---|---|
| source URL（公開済 public VOD） | 記録 |
| source title | 記録 |
| VOD public status（public / unlisted / private） | public のみ |
| paid / members-only / concert footage では無いことの operator readback | 確認済み |
| 第三者 IP / game / music リスク | 該当の有無と内訳 |
| description draft candidate に source URL / source title を入れられるか | yes / weak |
| publish acceptance ではないこと | 維持（`production_candidate=false`） |

## Acceptance（HoloEN-01 done 条件）

1. HoloEN public VOD URL が **避けるべき素材条件** を満たさないと assistant または operator が readback 済み
2. URL → source_video.mp4 → source.wav → transcript.json → edit_pack.json → rendered_video.mp4 → nle_cut_list.csv まで exit 0
3. `audit-material-ledger ok=true`
4. rendered video の FFprobe metadata が render manifest と一致
5. source attribution（source URL / source title）が `rights_manifest.json` の `source_video.url` / `source_video.title` と receipt / CSV に保持
6. Quality scorecard が技術 / 制作 / 権利 の 3 軸で記入済み
7. `production_candidate=false` / `creative_acceptance=false` / `publish_acceptance=false` を維持
8. すべての smoke artifact が ignored `episodes/$EP/` 配下に閉じている
9. 観測結果に基づき次候補（JP-STT-01 / transcript review / production render acceptance 等）を 1 つ推奨する

## Smoke 結果（初回 actual smoke）

assistant 自律選定 URL: **<https://www.youtube.com/watch?v=D4i4fjs9PWc>** — 【Kroniicle Animation】 Wisdom Teeth Removal Woes（Ouro Kronii オリジナル animation、77.78s、public、members-only / paid / concert / song 非該当、第三者 IP リスク低）

ignored episode: `episodes/holoen01_kronii_wisdomteeth_20260520/`

### Pipeline trace（全 exit 0）

1. `fetch-source-video --mode yt-dlp-video` → `source_video.mp4` (h264 / aac / 1920x1080 / 60fps / 77.78s)
2. `fetch-source-audio --mode yt-dlp-audio` → `source.wav` (pcm_s16le / 16kHz / mono)
3. `transcribe-audio --engine vosk --language en --model vosk-model-small-en-us-0.15` → 13 segments / 66.2% coverage / real_transcript=true
4. `init-edit-pack` + `generate-cuts --target-duration-seconds 15 --gap-threshold-seconds 3 --select-generated` → 4 cut candidates
5. `check-cut-context` → 2 passed / 2 needs_review
6. `generate-subtitles --wrap-eaw 40 --selected-cuts-only` → 13 subtitle drafts、`source_type=real_transcript`
7. `render-tiny-proof --burn-in-subtitles diagnostic` → `rendered_video.mp4` 4.89s / 1080p / h264 / aac / subtitle burn-in enabled
8. `export-nle` → `nle_cut_list.csv` 4 rows / `nle_export_manifest.json` / `nle_export_report.html`
9. `audit-material-ledger` → ok=true / 0 issues / 2 materials

### Quality scorecard readback

| 軸 | 評価 | コメント |
|---|---|---|
| 技術: pipeline 全 exit 0 | ✅ pass | 全段 exit 0 |
| 技術: ledger audit | ✅ pass | ok=true |
| 技術: transcript coverage | weak-pass | 66.2%（Big Buck Bunny 0.2% から段違い改善） |
| 技術: rendered video metadata | ✅ pass | 1080p/60fps/h264/aac、字幕焼き込み有効 |
| 制作: transcript 自然さ | **weak** | `i'm not deflating on your way` 等、誤認識多い。Kroniicle Animation の voice acting tone + BGM が STT 精度を下げている可能性 |
| 制作: subtitle 自然さ | **weak** | transcript と同根 |
| 制作: cut candidate 面白さ | **needs_review** | 4 cuts 中 2 が `needs_review` |
| 制作: cut テンポ | ✅ pass | 4.89 / 17.40 / 19.98 / 20.85s |
| 制作: NLE 投稿候補性 | **weak** | STT 精度が編集起点として弱い |
| 権利: URL public / not paid / not concert / not song / 第三者 IP 低 | ✅ pass | Kronii original Kroniicle animation |
| 権利: attribution 保持 | ✅ pass | source URL + title が receipt / CSV に保持 |
| 権利: publish acceptance | ❌ 不該当（維持） | `production_candidate=false` 全 receipt 維持 |

### 観測された次の判断点

1. **STT 精度が weak**: Vosk EN small model は HoloEN voice acting / animation tone でも改善余地大。Phase 1.5 候補として whisper.cpp / OpenAI Whisper の比較がありえる
2. **cut boundary needs_review**: 4/2 が needs_review。context check の閾値調整 or transcript review workflow（ED-09 系）が next bottleneck
3. **rendered video 1080p / 60fps**: HoloEN source quality はそのまま保持される。production render acceptance / typography polish は別 slice
4. **権利 readback** は INVARIANTS 通り hard gate にしていない。`rights_status=pending` warning は出るが pipeline 停止しない

## 次候補の判断

HoloEN pilot を smoke した結果で、次のいずれかに進む：

| 観測 | 次候補 |
|---|---|
| transcript / subtitle / cut が成立 | `transcript review / correction` または `production render acceptance` |
| STT 品質が weak（Vosk EN が拾えない単語が多い） | 他 EN STT provider（Whisper.cpp 等）、または transcript correction |
| URL 未指定で blocked のまま | operator にHoloEN public VOD URL の選定を依頼 |
| 日本語展開が主目的になったら | `JP-STT-01 Japanese STT adapter smoke` |
| media pipeline は通るが品質が weak | human quality gate / review workflow |

Phase 0.5 はあくまで **「動画コンテンツとして成立しそうか」の早期診断**。配管検証から品質検証へ一段進む位置づけ。
