# JP-STT-01 — Japanese STT smoke runbook (vosk-model-ja)

`Phase 0` で URL → media → STT → cut/subtitle → diagnostic render → CSV の縦糸が通ったが、`vosk-model-small-en-us-0.15` は日本語コンテンツを transcribe できない。本 slice は **日本語 STT を Vosk JP model で接続する plumbing proof** であり、STT 品質受容 / creative acceptance / publishing acceptance ではない。

既存 Vosk adapter（`src/integrations/stt/vosk_adapter.py`、ED-07b）は language-agnostic であり、JP model を `--model` に指定して `--language ja` を渡せば動く。

## このスライスの境界

- **やる**: vosk-model-ja を使った日本語音声 → `transcript.json` の plumbing proof
- **やらない**: STT 品質評価、話者分離、transcript correction UI、日本語字幕 typography polish、production render acceptance、HoloEN-01 を JP 化した publish-quality 観測（別 slice）、whisper.cpp / OpenAI Whisper 等の他 provider、GUI button、Publishing

## Model 入手

| 項目 | 値 |
|---|---|
| 推奨 model | `vosk-model-small-ja-0.22`（small variant、軽量） |
| Download URL | <https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip> |
| サイズ目安 | ~50〜80 MB |
| ライセンス | Apache 2.0（alphacephei.com で確認） |
| 配置先 | `_tmp/stt_models/vosk-model-small-ja-0.22/` |
| 代替候補 | `vosk-model-ja-0.22` (big variant、約 1 GB、より高精度) — 必要時 |

### 手順

```powershell
mkdir -Force _tmp/stt_models | Out-Null
Invoke-WebRequest `
  -Uri 'https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip' `
  -OutFile '_tmp/stt_models/vosk-model-small-ja-0.22.zip' `
  -UseBasicParsing
Expand-Archive `
  -Path '_tmp/stt_models/vosk-model-small-ja-0.22.zip' `
  -DestinationPath '_tmp/stt_models/' -Force
```

`_tmp/stt_models/vosk-model-small-ja-0.22/` 配下に `am` / `conf` / `graph` / `ivector` ディレクトリが揃えば OK。

リンク切れの場合は <https://alphacephei.com/vosk/models> の Models ページから JP small variant を選定し、URL を更新する。

## JP audio source 候補

| 候補 | 推奨度 | rights / 第三者 IP | 備考 |
|---|:---:|---|---|
| **Windows TTS で生成した日本語 WAV** | ★★★（推奨） | 完全クリア（自己生成） | Phase 0 OUT-01e の実証済経路、再現性高、setup 最小。`ja-JP` voice が PC に入っている前提 |
| public domain 日本語 audio（青空文庫朗読等） | ★★ | クリア（PD） | アクセス手順がやや煩雑 |
| operator 手持ちの日本語音声 | ★★ | operator-owned | rights / 公開可否は operator 責任 |
| **HoloEN 等 VTuber 公開 VOD** | ★（本 slice では使わない） | guideline 確認必要 | publish-quality 観測は別 slice（JP-Pilot-01 等） |

本 slice の actual smoke は **Windows TTS 生成 WAV** を推奨。理由：

- 第三者 IP リスクなし
- 再現性が高い（短時間で再生成可能）
- plumbing proof 用途には十分

### Windows TTS で日本語 WAV を生成する例

```powershell
$tts = New-Object -ComObject SAPI.SpVoice
$stream = New-Object -ComObject SAPI.SpFileStream

# 16-bit PCM mono 16000Hz format（Vosk が直接読める形）
$fmt = New-Object -ComObject SAPI.SpAudioFormat
$fmt.Type = 22   # SAFT16kHz16BitMono
$stream.Format = $fmt
$stream.Open('_tmp/jp_tts_sample.wav', 3, $false)

# ja-JP voice を選択（OS にインストール済み前提）
$tts.Voice = ($tts.GetVoices() | Where-Object { $_.GetAttribute('Language') -match '0411|411' } | Select-Object -First 1)
$tts.AudioOutputStream = $stream

# 10〜15 秒程度の連続発話を読み上げる
$tts.Speak("こんにちは、これは日本語の音声認識テストです。ClipPipeGen の Vosk JP モデルで transcript を生成できるか確認します。")
$stream.Close()
```

`ja-JP` voice が無い場合は Windows Settings → Time & Language → Speech → "Add a voice" で日本語を追加する。代替として VOICEVOX 等の OSS TTS、または青空文庫朗読音源を使う。

## Smoke 手順

```powershell
# operator 変数
$EP="jp_stt_smoke_<date>"   # ignored episode id
$MID_A="src_audio_jp_stt_smoke"
$JP_MODEL="_tmp/stt_models/vosk-model-small-ja-0.22"
$JP_WAV="_tmp/jp_tts_sample.wav"
$FFMPEG="<resolved ffmpeg path>"

# 1. episode skeleton
python -m src.cli.main init-episode --episode-id $EP

# 2. source.wav 登録（local-media-audio mode）
python -m src.cli.main fetch-source-audio --mode local-media-audio `
  --episode-id $EP --material-id $MID_A `
  --local-media $JP_WAV --ffmpeg-path $FFMPEG

# 3. JP transcribe（uvx --with vosk 経由）
uvx --with vosk python -m src.cli.main transcribe-audio `
  --episode-id $EP `
  --source-audio episodes/$EP/materials/$MID_A/source.wav `
  --output episodes/$EP/transcript.json `
  --engine vosk --model $JP_MODEL --language ja `
  --material-ledger episodes/$EP/material_ledger.json `
  --material-id $MID_A
```

## Readback 項目

`transcript.json` から readback する必須項目：

| field | 期待値 |
|---|---|
| `language` | `"ja"` |
| `stt.provider` | `"vosk"` |
| `stt.engine` | `"vosk"` |
| `stt.model` | JP model path（`_tmp/stt_models/vosk-model-small-ja-0.22` を含む） |
| `stt.params.language` | `"ja"` |
| `stt.real_transcript` | `true` |
| `segment_count` | `> 0`（Windows TTS で 10〜15 秒なら 1〜3 segment 程度） |
| `segments[0].text` | 日本語文字を含む文字列 |

CLI text フォーマットでも以下が確認できる：

```
created: episodes/<EP>/transcript.json
segments: <count>
duration_seconds: <wav duration>
provider: vosk
engine: vosk
model: _tmp/stt_models/vosk-model-small-ja-0.22
real_transcript: true
warning: real STT plumbing proof only; transcript quality is not creative acceptance
```

readback 後は ignored `episodes/<EP>/transcript.json` を覗いて `segments[].text` が日本語の妥当な文字列を含むかを目視確認する（completeness は acceptance 対象外）。

## Closure 条件（JP-STT-01 = done）

1. `uvx pytest -q` 全 pass（JP variant test 含む）
2. `npm run smoke` / `npm run smoke:electron` OK
3. `git diff --check` clean
4. `vosk-model-small-ja-0.22` を operator が download / 展開済
5. Windows TTS（または同等の JP audio source）で生成した日本語 WAV を input に `transcribe-audio --engine vosk --language ja --model <jp path>` が exit 0
6. `transcript.json` の上記 readback 項目が期待通り
7. `production_candidate=false` 維持、すべての smoke artifact は ignored `episodes/jp_stt_smoke_<date>/` 配下
8. docs（FEATURE_REGISTRY / RUNTIME_STATE / HANDOFF / README）を JP-STT-01 done と HoloEN-01 done の状態に更新
9. commit + push `origin/main`

## トラブルシュート

| 症状 | 対処 |
|---|---|
| `transcribe-audio` が exit 1 で `Vosk input must be mono 16-bit PCM WAV` | source.wav が stereo / 8-bit になっている。`fetch-source-audio --mode local-media-audio` で正規化されているか確認 |
| `Vosk produced no transcript segments` warning | input WAV が短すぎる / 無音 / TTS voice が ja-JP でない可能性。10〜15 秒の連続発話で再生成 |
| `provider 'vosk' is not importable` | `uvx --with vosk` で実行しているか確認。素の `python` だと vosk が import できない |
| Model path が None / 認識されない | `--model` に絶対パスまたは worktree からの相対 path を渡す。worktree 内に download した方が安全 |
| Windows TTS に ja-JP voice が無い | Settings → Time & Language → Speech → Add a voice で Japanese を追加、または VOICEVOX 等の OSS TTS、青空文庫朗読音源で代替 |

## Future（本 slice の Out of scope）

| ID 候補 | 概要 |
|---|---|
| **ED-07c** | done。`transcribe-audio --engine vosk` は model path basename から infer できる言語と `--language` を照合し、不一致なら transcript を書かずに失敗する |
| **JP-Pilot-01** | HoloEN-01 を JP 化リスコープした publish-quality diagnostic pilot（日本語コンテンツでの投稿品質観測） |
| transcript correction UI | operator が日本語 transcript を手で直す GUI |
| JP 字幕 typography / safe-area / font polish | OUT-01 系の next slice |
| Whisper.cpp / OpenAI Whisper 採用 | JP STT 精度比較が必要になったタイミングで |
