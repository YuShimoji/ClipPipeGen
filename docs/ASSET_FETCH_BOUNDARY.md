# Asset Fetch Boundary — INT-02b / INT-02c / INT-02d

INT-02b は **spec only**。実 downloader は実装しない。目的は、yt-dlp / FFmpeg を `asset_fetch` integration の内側に閉じ込め、Editing core / STT / rendering / GUI に漏らさないこと。

INT-02c はこの境界に従い、実 yt-dlp / network fetch へ進まず、既存ローカル media file を FFmpeg で `source.wav` に正規化する最小実装だけを追加する。

INT-02d は **spec only**。`yt-dlp-audio` の URL fetch contract を仕様化するが、yt-dlp 実行、network fetch、CLI mode 追加は行わない。詳細は [YTDLP_AUDIO_SPEC.md](YTDLP_AUDIO_SPEC.md) を正本とする。

SH-05 local-preview-pack は INT-02 の実 downloader ではない。既存 `fetch-source-audio --mode local-media-audio` の出力を downstream artifact に接続し、`preview_manifest.json` / read-only `preview_report.html` を生成する review surface である。SH-05 は rendered video preview、network fetch、GUI fetch button、cut / concat、subtitle burn-in、render / encode を実装しない。詳細は [PREVIEW_PACK.md](PREVIEW_PACK.md) を正本とする。

## 状態

| ID | 状態 | 成果 |
|---|---|---|
| INT-02 | proposed | 親機能。source audio / video 取得全体 |
| INT-02a | done | `fetch-source-audio --mode fake` による source audio 契約、sidecar、receipt、ledger 接続 |
| INT-02b | done | 実 downloader 前の責務境界と readback contract |
| INT-02c | done | `fetch-source-audio --mode local-media-audio`。ローカル media file を FFmpeg で `source.wav` に正規化 |
| INT-02d | done | `yt-dlp-audio` boundary spec only。URL fetch / network / yt-dlp / FFmpeg / receipt / rights / human / GUI / STT の責務を分離 |

## Tool 責務

| Tool / 層 | やる | やらない |
|---|---|---|
| yt-dlp | URL から元 media を取得する。取得元 URL、provider、format、生成された intermediate file を readback する | audio normalize、STT、cut、concat、subtitle burn-in、render、creative 判断 |
| FFmpeg | source audio を `source.wav` に正規化する。標準は PCM WAV / mono / 16kHz / 16-bit | URL 取得、STT、cut 候補抽出、文脈チェック、字幕焼き込み、動画 render / encode |
| `src/integrations/asset_fetch/` | yt-dlp / FFmpeg の実行 adapter、preflight、receipt 材料の収集 | pipeline 本体ロジック、Editing 判断、Publishing 判断 |
| `src/cli/fetch_source_audio.py` | asset_fetch adapter を呼び、`source.wav` / `sidecar.json` / `fetch_receipt.json` / `material_ledger` を接続する | STT を呼ぶ、cut/render を呼ぶ、URL mode と local file mode を混ぜる |
| `build-local-preview-pack` | 既存 `local-media-audio` / transcript / cut / context / subtitle contract を順に接続し、manifest/report を生成する | yt-dlp / FFmpeg を直接呼ぶ、network fetch、fetch-source-video、render / encode、GUI fetch button |
| `transcribe-audio` | 既存ローカル音声ファイルを `transcript.json` にする | URL / VOD 取得、yt-dlp / FFmpeg 呼び出し |
| Editing core | transcript から cut / context / subtitle artifact を作る | downloader、FFmpeg、render、encode |
| GUI | 実装済み safe action の readback を表示する | fetch button を追加する |

## 出力 Contract

`fetch-source-audio` の各 mode は、INT-02a fake と同じ material directory 形を守る。

| 出力 | 必須 | 内容 |
|---|---|---|
| `materials/<material_id>/source.wav` | yes | normalized source audio。PCM WAV / mono / 16kHz / 16-bit |
| `materials/<material_id>/sidecar.json` | yes | 出所、retrieval method、license / restrictions readback。権利判断の正本ではない |
| `materials/<material_id>/fetch_receipt.json` | yes | 実行 command、tool versions、provider、input、hash、warnings、stderr digest、rollback |
| `material_ledger.json` entry | yes | `kind="source_audio"`、`subkind="wav_pcm_16k_mono"`、`intended_uses=["editing_audio"]` |
| intermediate media file | optional | 残す場合は receipt と rollback に必ず記録する。INT-02c は intermediate を生成しない |

## Mode Contract

mode 名は、実装 commit で `FEATURE_REGISTRY` に登録してから CLI choices に追加する。

| mode 候補 | 状態 | 責務 |
|---|---|---|
| `fake` | implemented | network / yt-dlp / FFmpeg を呼ばず、1秒 silent WAV を作る |
| `local-media-audio` | implemented in INT-02c | 既存ローカル media file を FFmpeg で `source.wav` に正規化する。URL / VOD / network fetch はしない |
| `yt-dlp-audio` | specified in INT-02d, not implemented | URL から元 media を取得し、FFmpeg で `source.wav` に正規化する。取得と正規化以外はしない |
| `fetch-source-video` | future | 未実装。INT-02c の範囲外 |

実 mode は次を満たす。

1. `--dry-run` は subprocess / network を呼ばず、command plan / paths / expected outputs / conflicts を JSON で返す。
2. 実行後に `fetch_receipt.json` が required readback を持つ。
3. `material_ledger` refresh は同じ `material_id` に限定し、別 ID を削除しない。
4. rights status は receipt / ledger に snapshot するだけで hard gate にしない。
5. failure 時に partial outputs と rollback 対象が operator に見える。

## INT-02c 固定判断

| 項目 | INT-02c の判断 |
|---|---|
| FFmpeg path discovery | `--ffmpeg-path` → `CLIPPIPE_FFMPEG` → PATH の順。dry-run は発見だけ行い、subprocess は呼ばない |
| version 取得失敗 | 実行は失敗。`source.wav` / sidecar / receipt / ledger は作らない |
| duration readback | ffprobe は使わない。input duration は unknown warning、output WAV duration は Python `wave` で読む |
| `stderr_digest` | scrubbed stderr の SHA-256、tail、tail length、truncated flag。全文 stderr は保存しない |
| partial failure | FFmpeg normalize 失敗時は partial `source.wav` を削除する。sidecar / receipt / ledger は書かない |

## Readback Contract

receipt は INT-02a fields に加えて、以下を記録する。

| フィールド | 内容 |
|---|---|
| `provider` | `asset_fetch_fake` / `local-media` / future `yt-dlp` 等 |
| `tools[].name` | `ffmpeg` / future `yt-dlp` |
| `tools[].version` | 実行時に取得した version。version check 失敗時は INT-02c では失敗扱い |
| `commands[].summary` | secret を含まない command 概要 |
| `commands[].exit_code` | tool process の終了 code |
| `input.source_url` | URL 取得 mode の入力 URL。INT-02c では `null` |
| `input.local_path` | local media mode の入力 file |
| `outputs[].path` | 生成 file |
| `outputs[].sha256` | 生成 file hash |
| `outputs[].byte_size` | 生成 file size |
| `outputs[].duration_seconds` | 取得できる場合の media/audio duration |
| `warnings[]` | fallback、duration unknown、metadata 欠落など |
| `stderr_digest` | stderr 全文ではない digest / tail。秘密情報は scrub する |
| `rollback.files[]` | generated file / sidecar / receipt |
| `rollback.ledger_material_id` | rollback 時に消す ledger entry の ID |

## Hard Boundaries

| 禁止 | 理由 |
|---|---|
| `transcribe-audio` に URL / VOD fetch を足す | STT と素材取得を混ぜると再実行、権利 readback、失敗復旧が壊れる |
| `generate-cuts` / `check-cut-context` / `generate-subtitles` から FFmpeg を呼ぶ | Editing は transcript / edit_pack の変換層であり、media tool 実行層ではない |
| `asset_fetch` に cut / concat / subtitle burn-in / render / encode を入れる | OUT-01 / ED-06 の責務を侵食する |
| GUI に fetch button を先に追加する | preflight / receipt / rollback が operator-visible になる前に実行面を広げない |
| rights status を hard gate にする | rights は readback。取得可否の自動判断へ過剰遷移しない |
| creative acceptance / preview 判定を receipt に入れる | receipt は実行証跡。品質判断や採否は別 artifact / operator review |

## INT-02c 実装後に残る未決事項

| 項目 | 残り |
|---|---|
| yt-dlp discovery | `yt-dlp` path discovery、version failure、provider URL policy は未決 |
| URL fetch mode | `yt-dlp-audio` の exact CLI contract、intermediate media file の保存/削除 policy は未決 |
| source video | `fetch-source-video` は未実装 |
| real dependency acceptance | local operator smoke passed。実 FFmpeg `ffmpeg version 8.0.1-full_build-www.gyan.dev` で synthetic local WAV を `source.wav` に正規化し、Python `wave` readback、receipt、ledger audit、ignored artifact status を確認。CI は fake runner / monkeypatch に限定 |
| GUI | fetch button は未実装。追加する場合は preflight / confirmation / receipt readback の GUI contract が必要 |
| local preview pack | SH-05 実装済み。local media 1本から `preview_manifest.json` / read-only `preview_report.html` まで生成。これは artifact preview であり rendered video preview ではない |

## INT-02d yt-dlp-audio spec only

| 領域 | 固定境界 |
|---|---|
| URL fetch | future `yt-dlp-audio` の入力としてだけ扱う。`transcribe-audio` / Editing CLI / GUI には URL を渡さない |
| network access | actual 実装時の `src/integrations/asset_fetch/` adapter だけが行う。dry-run は network を呼ばない |
| yt-dlp | 元 media の一時取得と provider / extractor / format / warnings readback だけを担う |
| FFmpeg | yt-dlp が得た media を `source.wav` に正規化するだけ。cut / concat / render / encode はしない |
| receipt | URL、provider、yt-dlp / FFmpeg versions、commands、outputs、warnings、stderr digest、rollback を保存する |
| rights | status / warnings は snapshot するだけで hard gate にしない |
| human responsibility | URL 選定、権利・規約 review、公開可否、creative acceptance は人間責務 |
| GUI | INT-02d では fetch button を追加しない |
| STT | `transcribe-audio` は生成済みローカル `source.wav` だけを読む |

## Test 観点

実装前後に最低限確認する。

1. dry-run は network / subprocess を呼ばず、command plan と conflicts を返す。
2. success は `source.wav`、sidecar、receipt、ledger entry を生成する。
3. receipt は tool versions、commands、input、outputs、hash、duration、warnings、stderr digest、rollback を持つ。
4. duplicate material は `--force` なしで拒否し、`--force` は同じ material ID だけ refresh する。
5. rights status は pending / failed でも hard gate にならない。
6. `transcribe-audio` は URL を拒否し続ける。
7. `src/pipeline/*` と Editing/STT CLI は `ffmpeg` / `yt-dlp` を直接参照しない。
8. GUI smoke は fetch button 追加なしで通る。

## 次に進む条件

INT-02c 後に次へ進む場合は、`yt-dlp-audio` の URL fetch だけを別 slice として扱う。`fetch-source-video`、render、encode、GUI action はさらに別 slice に分ける。
