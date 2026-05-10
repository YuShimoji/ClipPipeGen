# Asset Fetch Boundary — INT-02b

INT-02b は **spec only**。実 downloader は実装しない。目的は、yt-dlp / FFmpeg を `asset_fetch` integration の内側に閉じ込め、Editing core / STT / rendering / GUI に漏らさないこと。

## 状態

| ID | 状態 | 成果 |
|---|---|---|
| INT-02 | proposed | 親機能。source audio / video 取得全体 |
| INT-02a | done | `fetch-source-audio --mode fake` による source audio 契約、sidecar、receipt、ledger 接続 |
| INT-02b | done | 本ドキュメント。実 downloader 前の責務境界と readback contract |

## Tool 責務

| Tool / 層 | やる | やらない |
|---|---|---|
| yt-dlp | URL から元 media を取得する。取得元 URL、provider、format、生成された intermediate file を readback する | audio normalize、STT、cut、concat、subtitle burn-in、render、creative 判断 |
| FFmpeg | source audio を `source.wav` に正規化する。標準は PCM WAV / mono / 16kHz / 16-bit | URL 取得、STT、cut 候補抽出、文脈チェック、字幕焼き込み、動画 render / encode |
| `src/integrations/asset_fetch/` | yt-dlp / FFmpeg の実行 adapter、preflight、receipt 材料の収集 | pipeline 本体ロジック、Editing 判断、Publishing 判断 |
| `src/cli/fetch_source_audio.py` | asset_fetch adapter を呼び、`source.wav` / `sidecar.json` / `fetch_receipt.json` / `material_ledger` を接続する | 実装済み mode 以外を silent fallback する、STT を呼ぶ、cut/render を呼ぶ |
| `transcribe-audio` | 既存ローカル音声ファイルを `transcript.json` にする | URL / VOD 取得、yt-dlp / FFmpeg 呼び出し |
| Editing core | transcript から cut / context / subtitle artifact を作る | downloader、FFmpeg、render、encode |
| GUI | 実装済み safe action の readback を表示する | INT-02b 時点で fetch button を追加しない |

## 出力 Contract

`fetch-source-audio` の実 downloader mode も、INT-02a fake と同じ material directory 形を守る。

| 出力 | 必須 | 内容 |
|---|---|---|
| `materials/<material_id>/source.wav` | yes | normalized source audio。PCM WAV / mono / 16kHz / 16-bit |
| `materials/<material_id>/sidecar.json` | yes | 出典、retrieval method、license / restrictions readback。権利判断の正本ではない |
| `materials/<material_id>/fetch_receipt.json` | yes | 実行 command、tool versions、provider、URL、hash、warnings、stderr digest、rollback |
| `material_ledger.json` entry | yes | `kind="source_audio"`、`subkind="wav_pcm_16k_mono"`、`intended_uses=["editing_audio"]` |
| intermediate media file | optional | 残す場合は receipt と rollback に必ず記録する。残さない場合も receipt に処理概要を残す |

## Future Mode Contract

実 downloader を追加する場合の mode 名は、実装 PR / commit で `FEATURE_REGISTRY` に登録してから使う。

| mode 候補 | 状態 | 責務 |
|---|---|---|
| `fake` | implemented | network / yt-dlp / FFmpeg を呼ばず、1秒 silent WAV を作る |
| `yt-dlp-audio` | future | URL から media を取得し、FFmpeg で `source.wav` に正規化する |
| `local-media-audio` | future | 既存ローカル media file を FFmpeg で `source.wav` に正規化する。URL 取得はしない |

future mode は次を満たすまで CLI choices に追加しない。

1. `--dry-run` が command plan / paths / expected outputs / conflicts を JSON で返す。
2. 実行後に `fetch_receipt.json` が required readback を持つ。
3. `material_ledger` refresh は同じ `material_id` に限定し、別 ID を削除しない。
4. rights status は receipt / ledger に snapshot するだけで hard gate にしない。
5. failure 時に partial outputs と rollback 対象が operator に見える。

## Readback Contract

実 downloader receipt は INT-02a fields に加えて、以下を記録する。

| フィールド | 内容 |
|---|---|
| `provider` | `yt-dlp` / `local-media` 等 |
| `tools[].name` | `yt-dlp` / `ffmpeg` |
| `tools[].version` | 実行時に取得した version。不明なら `unknown` |
| `commands[].summary` | secret を含まない command 概要 |
| `commands[].exit_code` | tool process の終了 code |
| `input.source_url` | URL 取得 mode の入力 URL |
| `input.local_path` | local media mode の入力 file |
| `outputs[].path` | 生成 file |
| `outputs[].sha256` | 生成 file hash |
| `outputs[].byte_size` | 生成 file size |
| `outputs[].duration_seconds` | 取得できる場合の media/audio duration |
| `warnings[]` | fallback、duration 不明、metadata 欠落など |
| `stderr_digest` | stderr 全文ではなく digest / tail。秘密情報を保存しない |
| `rollback.files[]` | generated / retained intermediate / sidecar / receipt |
| `rollback.ledger_material_id` | rollback 時に消す ledger entry の ID |

## Hard Boundaries

| 禁止 | 理由 |
|---|---|
| `transcribe-audio` に URL / VOD fetch を足す | STT と素材取得を混ぜると再実行・権利 readback・失敗復旧が壊れる |
| `generate-cuts` / `check-cut-context` / `generate-subtitles` から FFmpeg を呼ぶ | Editing は transcript / edit_pack の変換層であり、media tool 実行層ではない |
| `asset_fetch` に cut / concat / subtitle burn-in / render / encode を入れる | OUT-01 / ED-06 の責務を侵食する |
| GUI に fetch button を先に追加する | preflight / receipt / rollback が operator-visible になる前に実行面を広げると事故点が増える |
| rights status を hard gate にする | rights は readback。取得可否の自動判断へ過剰委譲しない |
| creative acceptance / preview 判定を receipt に入れる | receipt は実行証跡。品質判断や採否は別 artifact / operator review |

## 実 downloader 前の未決事項

| 項目 | 決めること |
|---|---|
| dependency discovery | `yt-dlp` / `ffmpeg` の path 指定、PATH fallback、version 取得失敗時の扱い |
| mode name | `yt-dlp-audio` を採用するか、provider-neutral な別名にするか |
| intermediate file policy | 元 media を保存するか、一時 file として消すか。保存する場合の ledger kind |
| stderr digest | digest algorithm、tail 文字数、secret scrub 方針 |
| duration readback | FFprobe を使うか、FFmpeg output parse に留めるか |
| provider URL policy | YouTube 以外の URL を受けるか、preflight warning に留めるか |
| failure cleanup | partial file を残して rollback に出すか、削除して warning に残すか |
| tests | fake subprocess adapter で command plan / receipt / rollback / no-core-import を確認する |

## Test 観点

実 downloader 実装前後に最低限確認する。

1. dry-run は network / subprocess を呼ばず、command plan と conflicts を返す。
2. success は `source.wav`、sidecar、receipt、ledger entry を生成する。
3. receipt は tool versions、commands、input、outputs、hash、duration、warnings、stderr digest、rollback を持つ。
4. duplicate material は `--force` なしで拒否し、`--force` は同じ material ID だけ refresh する。
5. rights status は pending / failed でも hard gate にならない。
6. `transcribe-audio` は URL を拒否し続ける。
7. `src/pipeline/*` と Editing/STT CLI は `ffmpeg` / `yt-dlp` を直接参照しない。
8. GUI smoke は fetch button 追加なしで通る。

## 次に進む条件

INT-02b 後に実装へ進む場合は、上記未決事項を閉じたうえで、最初の実装を **source audio の実取得と正規化だけ**に絞る。`fetch-source-video`、render、encode、GUI action は別 slice に分ける。
